import os
import time
import cv2
import zxingcpp
import numpy as np


def _ensure_dir(d):
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass


def enhanced_read_barcodes(img_bgr, *, debug=False, save_dir='/tmp/pdf417_debug',
                           scales=(0.75, 1.0, 1.5, 2.0), rotations=(0, -10, -5, 5, 10, 90, 180, 270),
                           formats=None, # optional iterable of zxingcpp barcode formats to accept (e.g. [zxingcpp.PDF417])
                           save_failed=False):
    """Attempt to read barcodes using zxingcpp applying multiple scales,
    rotations and preprocessing variants. Returns a list of (result, meta) where
    meta contains 'scale', 'rotation', 'preproc'."""
    results = []
    _ensure_dir(save_dir) if debug else None

    # Prepare preprocessing variants as callables returning BGR images
    def preproc_none(img):
        return img

    def preproc_clahe(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        res = clahe.apply(gray)
        return cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)

    def preproc_bilateral(img):
        return cv2.bilateralFilter(img, 9, 75, 75)

    def preproc_denoise(img):
        # fastNlMeans for color images
        try:
            return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        except Exception:
            return img

    def preproc_morph(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        return cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)

    def preproc_hist_color(img):
        # Equalize each channel independently in YUV space
        try:
            yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        except Exception:
            return img

    def preproc_unsharp(img):
        gaussian = cv2.GaussianBlur(img, (0,0), sigmaX=3)
        return cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)

    def preproc_thresh(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
        return cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)

    preprocessors = [
        ('none', preproc_none),
        ('clahe', preproc_clahe),
        ('bilateral', preproc_bilateral),
        ('unsharp', preproc_unsharp),
        ('thresh', preproc_thresh),
        ('denoise', preproc_denoise),
        ('morph', preproc_morph),
        ('hist_color', preproc_hist_color)
    ]

    h0, w0 = img_bgr.shape[:2]
    attempt = 0
    for scale in scales:
        sw = max(1, int(w0 * scale))
        sh = max(1, int(h0 * scale))
        img_scaled = cv2.resize(img_bgr, (sw, sh), interpolation=cv2.INTER_LINEAR)
        for pname, preproc in preprocessors:
            proc = preproc(img_scaled)
            for rot in rotations:
                attempt += 1
                if rot != 0:
                    M = cv2.getRotationMatrix2D((proc.shape[1]//2, proc.shape[0]//2), rot, 1.0)
                    img_var = cv2.warpAffine(proc, M, (proc.shape[1], proc.shape[0]))
                else:
                    img_var = proc

                # zxingcpp expects RGB arrays
                try:
                    img_rgb = cv2.cvtColor(img_var, cv2.COLOR_BGR2RGB)
                except Exception:
                    img_rgb = img_var

                try:
                    # try reading barcodes; can restrict to formats if requested
                    res = zxingcpp.read_barcodes(img_rgb)
                    if formats:
                        res = [r for r in res if getattr(r, 'format', None) in formats]
                except Exception as e:
                    # If zxingcpp fails on some images, ignore and keep trying
                    res = []

                if res:
                    for r in res:
                        meta = {'scale': scale, 'rotation': rot, 'preproc': pname, 'attempt': attempt}
                        results.append((r, meta))
                    # If debug, save image that succeeded
                    if debug:
                        ts = int(time.time() * 1000)
                        fname = os.path.join(save_dir, f'success_{ts}_{attempt}_{pname}_{rot}.jpg')
                        try:
                            cv2.imwrite(fname, img_var)
                        except Exception:
                            pass
                    # return early with successful results (prioritize first hits)
                    return results

                # debug save candidate
                if debug:
                    ts = int(time.time() * 1000)
                    fname = os.path.join(save_dir, f'cand_{ts}_{attempt}_{pname}_{rot}.jpg')
                    try:
                        cv2.imwrite(fname, img_var)
                    except Exception:
                        pass

    return results
