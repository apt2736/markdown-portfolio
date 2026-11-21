---
layout: default
title: Bird's Eye View Autotuner with RealSense using RANSAC Plane Regression
---

# Bird's Eye View Autotuner with RealSense using RANSAC Plane Regression

## Introduction

On our 1:10 scale autonomous car, lane detection, obstacle projection, and lookahead steering run on a top-down Bird's Eye View (BEV) image warped from a front-mounted RGB-D camera. A standard 4-point perspective warp maps four trapezoid corners in the camera image to a rectangle on the BEV canvas. When those corners are picked manually or computed from a fixed mounting angle, small physical changes break the alignment. Suspension sag, battery swaps, or a slight bump to the camera mount shifts camera pitch, roll, and height above the track, causing parallel lane markings to converge or diverge in the warped view and skewing lookahead distances.

Recalibrating four image corners by hand before every run is slow and inconsistent. We address this with an automatic extrinsic and BEV calibration pipeline driven by the camera's depth stream. From a single aligned depth frame, the routine reconstructs a 3D point cloud, fits the ground plane through axis-constrained Random Sample Consensus (RANSAC), builds an orthonormal camera-to-chassis rotation basis via Gram-Schmidt orthogonalization, and projects a metric ground rectangle through the calibrated transform to synthesize the BEV homography matrix.

## How it Works

Let $D(u, v) \in \mathbb{Z}\_{\ge 0}$ be the depth reading at pixel coordinates $(u, v)$ from the aligned depth frame, and let $(f\_x, f\_y, c\_x, c\_y)$ be the pinhole intrinsic parameters of the camera optical frame (where $+X\_c$ points right, $+Y\_c$ points down, and $+Z\_c$ points forward along the optical axis).

Pixels with missing zero depth or far-field readings beyond the usable range limit $z\_{\max}$ are discarded. Each valid reading is converted to metric depth $z\_c \in (0, z\_{\max}]$ and back-projected into a 3D point $\mathbf{p}\_c = [x\_c, y\_c, z\_c]^T$ in the camera optical coordinate frame:

$$
\mathbf{p}_c = \begin{bmatrix} x_c \\ y_c \\ z_c \end{bmatrix} = \begin{bmatrix} \dfrac{u - c_x}{f_x} z_c \\ \rule{0pt}{1.6em}\dfrac{v - c_y}{f_y} z_c \\ \rule{0pt}{1.2em} z_c \end{bmatrix}, \qquad 0 \lt z_c \le z_{\max}
$$

Because perspective projection concentrates far more pixels per unit ground area close to the vehicle than downrange, fitting a plane directly to the raw point cloud $\mathcal{P}\_{\text{raw}}$ weights near-field noise heavily. We downsample $\mathcal{P}\_{\text{raw}}$ through a 3D voxel grid filter with isotropic leaf size $\ell\_{\text{vox}}$, producing a spatially uniform point set $\mathcal{P}\_{\text{vox}}$ that balances near- and far-field floor coverage while keeping RANSAC iteration cost low.

In the camera optical frame, the road surface is modeled as a plane with coefficient vector $\boldsymbol{\pi} = [A, B, C, D]^T$:

$$
A x_c + B y_c + C z_c + D = 0
$$

To keep track walls or vertical barriers from being mistaken for the road, segmentation applies an axis-constrained RANSAC plane model over iteration budget $N\_{\text{iter}}$ with an inlier distance threshold $\delta\_{\text{inlier}}$. Because $+Y\_c$ points downward in the optical frame, the nominal upward floor normal aligns with reference axis $\mathbf{a}\_{\text{ref}} = [0, -1, 0]^T$. Candidate planes sampled from minimal 3-point subsets are accepted only when their normal lies within angular tolerance $\epsilon\_\theta$ of $\mathbf{a}\_{\text{ref}}$, and the hypothesis maximizing the inlier set $\mathcal{I}(\boldsymbol{\pi})$ is refined over all inliers:

$$
\boldsymbol{\pi}^\ast = \arg\max_{\boldsymbol{\pi}} \lvert \mathcal{I}(\boldsymbol{\pi}) \rvert, \qquad \mathcal{I}(\boldsymbol{\pi}) = \left\lbrace \mathbf{p}_c \in \mathcal{P}_{\text{vox}} \;\middle|\; \frac{\lvert A x_c + B y_c + C z_c + D \rvert}{\sqrt{A^2 + B^2 + C^2}} \le \delta_{\text{inlier}} \right\rbrace
$$

Dividing $\boldsymbol{\pi}^\ast$ by the Euclidean norm $\sqrt{A^2 + B^2 + C^2}$ yields unit-normal plane coefficients $[\hat{A}, \hat{B}, \hat{C}, \hat{D}]^T$:

$$
\begin{bmatrix} \hat{A} \\ \hat{B} \\ \hat{C} \\ \hat{D} \end{bmatrix} = \frac{1}{\sqrt{A^2 + B^2 + C^2}} \begin{bmatrix} A \\ B \\ C \\ D \end{bmatrix}
$$

Because $[\hat{A}, \hat{B}, \hat{C}, \hat{D}]^T$ and $[-\hat{A}, -\hat{B}, -\hat{C}, -\hat{D}]^T$ represent the same plane with inverted orientation, sign ambiguity is resolved by enforcing $\hat{B} \le 0$ so the unit normal $\hat{\mathbf{n}} = [\hat{A}, \hat{B}, \hat{C}]^T$ always points upward from the road (opposing $+Y\_c$):

$$
\begin{bmatrix} \hat{A} & \hat{B} & \hat{C} & \hat{D} \end{bmatrix}^T \leftarrow -\begin{bmatrix} \hat{A} & \hat{B} & \hat{C} & \hat{D} \end{bmatrix}^T \quad \text{if } \hat{B} \gt 0
$$

Under unit normalization, the perpendicular height of the camera optical center above the floor is $h\_{\text{cam}} = \lvert \hat{D} \rvert$. Estimates exceeding the physical mounting bound $h\_{\max}$ are rejected as degenerate fits.

Rather than solving for a single pitch angle and ignoring roll, we build a complete 3D orthonormal rotation basis $(\mathbf{e}\_x, \mathbf{e}\_y, \mathbf{e}\_z)$ linking the ground-aligned chassis frame ($+X\_b$ forward, $+Y\_b$ left, $+Z\_b$ upward normal to the road) to the camera optical frame. Setting the vertical axis $\mathbf{e}\_z = \hat{\mathbf{n}}$ and seeding the lateral reference vector along $\mathbf{v}\_y = [-1, 0, 0]^T$ (opposite the optical $+X\_c$ axis), Gram-Schmidt projection removes any tilt component along $\mathbf{e}\_z$ to form $\mathbf{e}\_y$, and the cross product $\mathbf{e}\_y \times \mathbf{e}\_z$ completes the right-handed forward axis $\mathbf{e}\_x$:

$$
\mathbf{e}_z = \begin{bmatrix} \hat{A} \\ \hat{B} \\ \hat{C} \end{bmatrix}, \qquad \mathbf{e}_y = \frac{\mathbf{v}_y - \left(\mathbf{v}_y \cdot \mathbf{e}_z\right)\mathbf{e}_z}{\left\lVert \mathbf{v}_y - \left(\mathbf{v}_y \cdot \mathbf{e}_z\right)\mathbf{e}_z \right\rVert_2}, \qquad \mathbf{e}_x = \frac{\mathbf{e}_y \times \mathbf{e}_z}{\left\lVert \mathbf{e}_y \times \mathbf{e}_z \right\rVert_2}
$$

Stacking $\mathbf{e}\_x^T, \mathbf{e}\_y^T, \mathbf{e}\_z^T$ as rows yields the rotation matrix $\mathbf{R}\_{b \leftarrow c} \in \mathrm{SO}(3)$, while the translation vector pairs the horizontal mounting offsets $(t\_x, t\_y)$ with the fitted ground height $t\_z = \lvert \hat{D} \rvert$:

$$
\mathbf{R}_{b \leftarrow c} = \begin{bmatrix} e_{x,x} & e_{x,y} & e_{x,z} \\ e_{y,x} & e_{y,y} & e_{y,z} \\ e_{z,x} & e_{z,y} & e_{z,z} \end{bmatrix}, \qquad \mathbf{t}_{b \leftarrow c} = \begin{bmatrix} t_x \\ t_y \\ \lvert \hat{D} \rvert \end{bmatrix}, \qquad \mathbf{T}_{b \leftarrow c} = \begin{bmatrix} \mathbf{R}_{b \leftarrow c} & \mathbf{t}_{b \leftarrow c} \\ \mathbf{0}^T & 1 \end{bmatrix}
$$

Broadcasting $\mathbf{T}\_{b \leftarrow c}$ updates the active extrinsic transform tree and yields the inverse transform $\mathbf{T}\_{c \leftarrow b} = \mathbf{T}\_{b \leftarrow c}^{-1}$, while storing the resulting translation and Euler angles $[\psi, \theta, \phi]^T$ so the calibration persists across restarts.

With $\mathbf{T}\_{c \leftarrow b}$ calibrated, the BEV warp is defined directly in metric ground coordinates rather than image pixels. On the road plane ($z\_b = 0$), a rectangular Region of Interest (ROI) of width $W\_g$ and length $L\_g$ starting at forward offset $x\_0$ defines four 3D ground corners $\mathbf{P}\_{b,i}$:

$$
\mathbf{P}_{b,\text{LB}} = \begin{bmatrix} x_0 \\ -W_g/2 \\ 0 \end{bmatrix}, \quad \mathbf{P}_{b,\text{RB}} = \begin{bmatrix} x_0 \\ W_g/2 \\ 0 \end{bmatrix}, \quad \mathbf{P}_{b,\text{LT}} = \begin{bmatrix} x_0 + L_g \\ -W_g/2 \\ 0 \end{bmatrix}, \quad \mathbf{P}_{b,\text{RT}} = \begin{bmatrix} x_0 + L_g \\ W_g/2 \\ 0 \end{bmatrix}
$$

Each corner $\mathbf{P}\_{b,i}$ is mapped into the camera optical frame via $\mathbf{P}\_{c,i} = \mathbf{R}\_{c \leftarrow b}\mathbf{P}\_{b,i} + \mathbf{t}\_{c \leftarrow b}$ and projected onto the 2D image plane through the camera intrinsics and distortion model $\Pi\_{\text{intr}}(\mathbf{P}\_{c,i})$ to obtain the four source vertices $\mathbf{s}\_i = [u\_i, v\_i]^T$ for $i \in \lbrace \text{LB}, \text{RB}, \text{LT}, \text{RT} \rbrace$. Pairing $\mathbf{s}\_i$ with fixed rectangular destination vertices $\mathbf{d}\_i$ on the $W\_{\text{BEV}} \times H\_{\text{BEV}}$ output canvas solves the $3 \times 3$ planar homography matrix $\mathbf{H}\_{\text{BEV}}$ used to warp incoming camera frames into a top-down view:

$$
\lambda_i \begin{bmatrix} \mathbf{d}_i \\ 1 \end{bmatrix} = \mathbf{H}_{\text{BEV}} \begin{bmatrix} \mathbf{s}_i \\ 1 \end{bmatrix}, \qquad I_{\text{BEV}}(x', y') = I_{\text{cam}}\!\left(\mathbf{H}_{\text{BEV}}^{-1}\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix}\right)
$$

The complete calibration and BEV homography routine is summarized in Algorithm 1:

$$
\begin{array}{l}
\hline
\textbf{Algorithm 1: } \text{RANSAC Ground-Plane Extrinsic Autotuning and BEV Homography Synthesis} \\
\hline
\textbf{Input: } D(u,v), \; (f_x, f_y, c_x, c_y, \mathbf{d}_{\text{dist}}), \; (z_{\max}, \ell_{\text{vox}}, h_{\max}), \; (\mathbf{a}_{\text{ref}}, \epsilon_\theta, \delta_{\text{inlier}}, N_{\text{iter}}), \; (x_0, W_g, L_g), \; \lbrace \mathbf{d}_i \rbrace \\
\textbf{Output: } \text{Calibrated transforms } (\mathbf{T}_{b \leftarrow c}, \mathbf{T}_{c \leftarrow b}) \text{ and BEV homography matrix } \mathbf{H}_{\text{BEV}} \\
\hline
\begin{array}{rl}
1: & \mathcal{P}_{\text{raw}} \leftarrow \emptyset \\
2: & \textbf{for each } \text{pixel } (u, v) \text{ with } 0 \lt z_c(u, v) \le z_{\max} \textbf{ do} \\
3: & \quad x_c \leftarrow (u - c_x)z_c / f_x, \quad y_c \leftarrow (v - c_y)z_c / f_y \\
4: & \quad \mathcal{P}_{\text{raw}} \leftarrow \mathcal{P}_{\text{raw}} \cup \lbrace [x_c, y_c, z_c]^T \rbrace \\
5: & \textbf{end for} \\
6: & \mathcal{P}_{\text{vox}} \leftarrow \operatorname{VoxelGridFilter}(\mathcal{P}_{\text{raw}}, \; \ell_{\text{vox}}) \\
7: & (\boldsymbol{\pi}^\ast, \mathcal{I}^\ast) \leftarrow \operatorname{RANSACParallelPlane}(\mathcal{P}_{\text{vox}}, \; \mathbf{a}_{\text{ref}}, \; \epsilon_\theta, \; \delta_{\text{inlier}}, \; N_{\text{iter}}) \\
8: & \textbf{if } \mathcal{I}^\ast = \emptyset \textbf{ then return } \text{CalibrationFailed} \\
9: & [\hat{A}, \hat{B}, \hat{C}, \hat{D}]^T \leftarrow \boldsymbol{\pi}^\ast / \sqrt{A^2 + B^2 + C^2} \\
10: & \textbf{if } \hat{B} \gt 0 \textbf{ then } [\hat{A}, \hat{B}, \hat{C}, \hat{D}]^T \leftarrow -[\hat{A}, \hat{B}, \hat{C}, \hat{D}]^T \textbf{ end if} \\
11: & \textbf{if } \lvert \hat{D} \rvert \gt h_{\max} \textbf{ then return } \text{CalibrationFailed} \\
12: & \mathbf{e}_z \leftarrow [\hat{A}, \hat{B}, \hat{C}]^T, \quad \mathbf{v}_y \leftarrow [-1, 0, 0]^T \\
13: & \mathbf{e}_y \leftarrow (\mathbf{v}_y - (\mathbf{v}_y \cdot \mathbf{e}_z)\mathbf{e}_z) / \lVert \mathbf{v}_y - (\mathbf{v}_y \cdot \mathbf{e}_z)\mathbf{e}_z \rVert_2, \quad \mathbf{e}_x \leftarrow (\mathbf{e}_y \times \mathbf{e}_z) / \lVert \mathbf{e}_y \times \mathbf{e}_z \rVert_2 \\
14: & \mathbf{R}_{b \leftarrow c} \leftarrow [\mathbf{e}_x, \; \mathbf{e}_y, \; \mathbf{e}_z]^T, \quad \mathbf{t}_{b \leftarrow c} \leftarrow [t_x, \; t_y, \; \lvert \hat{D} \rvert]^T \\
15: & \text{UpdateExtrinsicTransform}(\mathbf{R}_{b \leftarrow c}, \mathbf{t}_{b \leftarrow c}), \quad \mathbf{T}_{c \leftarrow b} \leftarrow \mathbf{T}_{b \leftarrow c}^{-1} \\
16: & \textbf{for each } \text{ground corner } i \in \lbrace \text{LB}, \text{RB}, \text{LT}, \text{RT} \rbrace \textbf{ do} \\
17: & \quad \mathbf{P}_{c,i} \leftarrow \mathbf{T}_{c \leftarrow b} \mathbf{P}_{b,i}, \quad \mathbf{s}_i \leftarrow \Pi_{\text{intr}}(\mathbf{P}_{c,i}) \\
18: & \textbf{end for} \\
19: & \mathbf{H}_{\text{BEV}} \leftarrow \operatorname{SolveHomography}(\lbrace \mathbf{s}_i \rbrace, \; \lbrace \mathbf{d}_i \rbrace)
\end{array} \\
\hline
\end{array}
$$

## Result

<div align="center">
  <video autoplay loop muted playsinline width="300">
    <source src="../../assets/images/auto_bev.mp4" type="video/mp4" />
  </video>
  <br>
  <sub>Bird's Eye View autotuning result</sub>
</div>
