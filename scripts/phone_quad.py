#!/usr/bin/env python3
"""Find the lit screen of a phone in a generated photo and print the CSS matrix3d that maps a UI of W x H design px onto the glass.

  python3 phone_quad.py phone.png --design 385 737 --stage-height 1080 --left -5

Why a homography and not a rotated rectangle: the camera sees the glass with slight perspective (top edge narrower than
bottom, sides not parallel). A flat rotated box overshoots on one side and the bezel looks wrong. This fits the four edges
(away from the rounded corners), intersects them for the true corners, and warps the UI onto them.
After applying it: put a black bezel ring on the UI (box-shadow: inset 0 0 0 5px #04060b, 0 0 0 3px #04060b) to hide the photo's
1-2 px blue fringe, keep the film grain UNDER the screen layer (grain on glass makes it look like a printed picture), and apply
the same handheld transform to the photo layer and the screen layer.
Needs: pip install opencv-python-headless numpy
"""
import argparse
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("image"); ap.add_argument("--design", nargs=2, type=float, default=[385, 737]); ap.add_argument("--stage-height", type=float, default=1080)
ap.add_argument("--left", type=float, default=0, help="x offset of the photo in the stage")
a = ap.parse_args()
im = cv2.imread(a.image)
H, W = im.shape[:2]
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
mask = ((hsv[..., 0] > 100) & (hsv[..., 0] < 125) & (hsv[..., 1] > 120) & (hsv[..., 2] > 90)).astype(np.uint8) * 255   # saturated-blue display
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
c = max(cnts, key=cv2.contourArea).reshape(-1, 2).astype(np.float32)
hull = cv2.convexHull(c.reshape(-1, 1, 2))
quad = cv2.approxPolyDP(hull, 0.015 * cv2.arcLength(hull, True), True).reshape(-1, 2).astype(np.float32)
s = quad.sum(1); d = quad[:, 1] - quad[:, 0]
Q = np.array([quad[np.argmin(s)], quad[np.argmin(d)], quad[np.argmax(s)], quad[np.argmax(d)]], np.float32)   # TL TR BR BL


def fit(p0, p1):
    ab = p1 - p0; L = np.linalg.norm(ab); u = ab / L; n = np.array([-u[1], u[0]])
    rel = c - p0; t = rel @ u / L; dist = rel @ n
    m = (t > 0.30) & (t < 0.70) & (np.abs(dist) < 0.07 * L)
    p = c[m]
    for _ in range(3):
        vx, vy, x0, y0 = cv2.fitLine(p, cv2.DIST_L2, 0, 0.01, 0.01).ravel()
        dd = np.abs((c - np.array([x0, y0])) @ np.array([-vy, vx]))
        m2 = m & (dd < 5)
        if m2.sum() > 20:
            p = c[m2]
    return np.array([x0, y0]), np.array([vx, vy])


def inter(l1, l2):
    (p1, d1), (p2, d2) = l1, l2
    t = np.linalg.solve(np.array([d1, -d2]).T, p2 - p1)
    return p1 + t[0] * d1


L = [fit(Q[0], Q[1]), fit(Q[1], Q[2]), fit(Q[2], Q[3]), fit(Q[3], Q[0])]
corners = np.array([inter(L[3], L[0]), inter(L[0], L[1]), inter(L[1], L[2]), inter(L[2], L[3])], np.float32)
k = a.stage_height / H
pts = corners * k + np.array([a.left, 0.0], np.float32)
Wd, Hd = a.design
Hm = cv2.getPerspectiveTransform(np.array([[0, 0], [Wd, 0], [Wd, Hd], [0, Hd]], np.float32), pts)
Hm /= Hm[2, 2]
m = [Hm[0, 0], Hm[1, 0], 0, Hm[2, 0], Hm[0, 1], Hm[1, 1], 0, Hm[2, 1], 0, 0, 1, 0, Hm[0, 2], Hm[1, 2], 0, Hm[2, 2]]
print("corners in stage px (TL TR BR BL):", pts.round(1).tolist())
print("transform-origin: 0 0;")
print("transform: matrix3d(" + ",".join(repr(round(float(x), 8)) for x in m) + ");")
