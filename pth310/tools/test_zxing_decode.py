#!/usr/bin/env python3
"""Simple tool to run `enhanced_read_barcodes` on images in a directory and report results.
Usage: python tools/test_zxing_decode.py <images_dir>
"""
import sys
import os
import time
import cv2
import zxingcpp
from zxing_utils import enhanced_read_barcodes


def test_dir(d):
    imgs = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not imgs:
        print('No images found in', d)
        return
    os.makedirs('/tmp/pdf417_test_results', exist_ok=True)
    for p in imgs:
        print('---', p)
        img = cv2.imread(p)
        if img is None:
            print('  unable to open')
            continue
        # test with debug true to save candidate images
        res = enhanced_read_barcodes(img, debug=True, save_dir='/tmp/pdf417_test_results', formats=[zxingcpp.PDF417])
        if not res:
            print('  No barcode found')
        else:
            for r, meta in res:
                print('  Found:', getattr(r, 'format', None), 'text_len=', len(getattr(r, 'text', '')))
                print('   meta:', meta)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: test_zxing_decode.py <images_dir>')
        sys.exit(1)
    test_dir(sys.argv[1])
