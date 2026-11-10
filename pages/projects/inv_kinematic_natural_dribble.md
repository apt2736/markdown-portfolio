---
layout: default
---

# Inverse Kinematic Feedforward Control with Ellipsoid Gain Profile for MSL Natural Dribbling

## Introduction

RoboCup Middle Size League (MSL) rules require Natural Dribbling: the ball must roll freely on the carpet in the direction of motion rather than being held stationary or spun backward during forward translation. On our robots, two spring-loaded dribbler arms handle the ball. Each arm is driven by an independent motor and instrumented with a Throttle Position Sensor (TPS) that measures mechanical arm deflection during contact.

<div align="center">
  <video autoplay loop muted playsinline width="360">
    <source src="../../assets/images/iris_ball_handling.mp4" type="video/mp4" />
  </video>
  <br>
  <sub>Example of natural dribble system (IRIS ITS)</sub>
</div>

Relying solely on closed-loop PID feedback over TPS deflection introduces phase lag. Because the ball must physically push the arms before the controller responds, rapid chassis acceleration causes delayed motor response and dropped balls. Adding a constant feedforward gain also fails because wheel-ball traction is directional: rolling forward pushes the ball, reversing pulls it against carpet resistance, and strafing slides across angled rollers. We address this with an inverse kinematics feedforward model shaped by a 2D ellipsoid gain profile, blended with the TPS PID controller.

## How it Works

MSL robots operate on a 2D plane, where the robot's commanded motion in its local body coordinate frame consists of lateral velocity $v_{lx}$ along the $x$-axis, longitudinal velocity $v_{ly}$ along the forward $y$-axis, and angular velocity $\omega_l$ around the vertical $z$-axis:

$$
\boldsymbol{q}_l = \begin{bmatrix} v_{lx} \\ v_{ly} \\ \omega_l \end{bmatrix}
$$

The dribbler mechanism comprises left ($L$) and right ($R$) compliant arms. When a ball enters the dribbler pocket, it pushes both arms upward. Let $\tau_i$ be the raw TPS reading for arm $i \in \{L, R\}$, with calibrated resting lower bound $\tau_{i,\min}$ and upper deflection bound $\tau_{i,\max}$. The sensor reading is first normalized into a deflection percentage $\tau_{\text{norm},i} \in [0, 100]$:

$$
\tau_{\text{norm},i} = \dfrac{\tau_i - \tau_{i,\min}}{\tau_{i,\max} - \tau_{i,\min}} \times 100, \qquad i \in \{L, R\}
$$

Because the dribbler arms pivot as they deflect, the effective contact angle $\alpha_i$ of each dribbler wheel relative to the ball varies linearly between its mechanical limits $\alpha_{\min}$ and $\alpha_{\max}$:

$$
\alpha_i = \alpha_{\min} + (\alpha_{\max} - \alpha_{\min})\dfrac{\tau_{\text{norm},i}}{100}, \qquad i \in \{L, R\}
$$

Let $C_b$ denote the ball circumference, $C_d$ denote the dribbler wheel circumference, and $r_b = \dfrac{C_b}{2\pi}$ denote the ball radius. The geometric transmission ratio $\gamma$ between the ball and each dribbler wheel is defined as:

$$
\gamma = \dfrac{C_b}{C_d}
$$

At contact angle $\alpha_i$, one unit revolution per second of the ball projects onto the robot's local $x$- and $y$-axes as the effective surface linear velocity components $[v_{bx,i}, v_{by,i}]^T$, which correspond to the projected angular factors $[\omega_{bx,i}, \omega_{by,i}]^T$ when divided by the ball radius $r_b$:

$$
\mathbf{v}_{b,i} = \begin{bmatrix} v_{bx,i} \\ v_{by,i} \end{bmatrix} = C_b \begin{bmatrix} \sin(\alpha_i) \\ \cos(\alpha_i) \end{bmatrix}, \qquad \boldsymbol{\omega}_{b,i} = \begin{bmatrix} \omega_{bx,i} \\ \omega_{by,i} \end{bmatrix} = \dfrac{1}{r_b}\mathbf{v}_{b,i}
$$

Using inverse kinematics, the translational feedforward components $[\omega_{\text{lin},x,i}, \omega_{\text{lin},y,i}]^T$ required by each dribbler wheel to match the robot's linear velocity $[v_{lx}, v_{ly}]^T$ are obtained by mapping each velocity component through $[\omega_{bx,i}, \omega_{by,i}]^T$ and scaling by $\gamma$:

$$
\boldsymbol{\omega}_{\text{lin},i} = \begin{bmatrix} \omega_{\text{lin},x,i} \\ \omega_{\text{lin},y,i} \end{bmatrix} = \gamma \begin{bmatrix} \dfrac{v_{lx}}{\omega_{bx,i} + \epsilon} \\ \rule{0pt}{1.8em}\dfrac{v_{ly}}{\omega_{by,i} + \epsilon} \end{bmatrix}, \qquad i \in \{L, R\}
$$

where $\epsilon = 10^{-4}$ is a small regularization constant introduced to avoid division by zero. When the robot rotates about its vertical $z$-axis at rate $\omega_l$, the dribbler wheels spin in opposite directions to pivot the ball in place:

$$
\begin{bmatrix} \omega_{\text{ang},L} \\ \omega_{\text{ang},R} \end{bmatrix} = \gamma \begin{bmatrix} -\omega_l \\ \omega_l \end{bmatrix}
$$

Ideal rolling without slip does not hold equally in all directions. Moving forward rolls the ball naturally, reversing requires pulling it against carpet friction, and strafing introduces sideways slip across the angled wheels. Instead of piecewise velocity switching, we shape the translational gain across all directions using a shifted 2D ellipsoid profile.

First, the robot's translational velocity heading $\psi$ is calculated relative to the forward local $+y$-axis and normalized to $[-\pi, \pi]$:

$$
\psi = \operatorname{atan2}(v_{ly}, \; v_{lx} + \epsilon) - \dfrac{\pi}{2}
$$

such that $\psi = 0$ corresponds to pure forward translation, $\psi = \pm\pi$ corresponds to backward translation, and $\psi = \mp\dfrac{\pi}{2}$ corresponds to lateral translation along $\pm x$. Let $r_x$ and $r_y$ be the lateral and longitudinal semi-axes of the gain ellipse, and let $\mathbf{o} = [o_x, o_y]^T$ be the ellipse center offset. Evaluating the parametric point on this shifted ellipse yields the directional gain vector $\mathbf{g}(\psi)$:

$$
\mathbf{g}(\psi) = \begin{bmatrix} g_x(\psi) \\ g_y(\psi) \end{bmatrix} = \begin{bmatrix} o_x + r_x \sin(\psi) \\ o_y + r_y \cos(\psi) \end{bmatrix}
$$

The scalar translational feedforward gain $K_{\text{lin}}(\psi)$ is then taken as the Euclidean norm of $\mathbf{g}(\psi)$:

$$
K_{\text{lin}}(\psi) = \|\mathbf{g}(\psi)\|_2 = \sqrt{g_x(\psi)^2 + g_y(\psi)^2}
$$

The center offset $o_y$ decouples forward gain ($\lvert o_y + r_y \rvert$ at $\psi = 0$) from backward pulling gain ($\lvert o_y - r_y \rvert$ at $\psi = \pm\pi$), while $r_x$ sets lateral responsiveness ($\psi = \mp\frac{\pi}{2}$) without abrupt gain jumps during diagonal motion.

Because the left and right dribbler wheels are mounted symmetrically across the robot's longitudinal axis, both wheels act in the same kinematic direction for longitudinal velocity ($\omega_{\text{lin},y,i}$) and in opposite directions for lateral velocity ($\pm\omega_{\text{lin},x,i}$). Scaling the linear terms by $K_{\text{lin}}(\psi)$ and the rotational terms by the angular gain $K_\theta$ produces:

$$
\begin{bmatrix} \omega_{\text{ff,lin},L} \\ \omega_{\text{ff,lin},R} \end{bmatrix} = K_{\text{lin}}(\psi) \begin{bmatrix} \omega_{\text{lin},y,L} + \omega_{\text{lin},x,L} \\ \omega_{\text{lin},y,R} - \omega_{\text{lin},x,R} \end{bmatrix}, \qquad \begin{bmatrix} \omega_{\text{ff,ang},L} \\ \omega_{\text{ff,ang},R} \end{bmatrix} = K_\theta \begin{bmatrix} \omega_{\text{ang},L} \\ \omega_{\text{ang},R} \end{bmatrix}
$$

Converting from $\text{rad/s}$ to $\text{deg/s}$ and negating the right channel to match its mirrored physical motor orientation yields the total feedforward velocity command $[u_{\text{ff},L}, u_{\text{ff},R}]^T$:

$$
\mathbf{u}_{\text{ff}} = \begin{bmatrix} u_{\text{ff},L} \\ u_{\text{ff},R} \end{bmatrix} = \dfrac{180}{\pi} \begin{bmatrix} \omega_{\text{ff,lin},L} + \omega_{\text{ff,ang},L} \\ -\left(\omega_{\text{ff,lin},R} + \omega_{\text{ff,ang},R}\right) \end{bmatrix}
$$

To handle disturbances like uneven turf or ball collisions, feedforward commands combine with a discrete PID loop on TPS deflection. The PID controller regulates deflection error ($e_L = \tau_{\text{norm},L} - \tau_{\text{sp},L}$ and $e_R = \tau_{\text{sp},R} - \tau_{\text{norm},R}$). When lateral velocity exceeds longitudinal velocity ($\lvert v_{lx} \rvert > 0.1\lvert v_{ly} \rvert$), setpoint $\tau_{\text{sp},i}$ increases to $90\%$ for firmer grip. With blending weight $\alpha_{\text{ff}}$, the wheel velocity setpoint sent to the low-level motor controller is:

$$
\mathbf{u}_{\text{sp}} = \begin{bmatrix} u_{\text{sp},L} \\ u_{\text{sp},R} \end{bmatrix} = (1 - \alpha_{\text{ff}})\mathbf{u}_{\text{fb}} + \alpha_{\text{ff}}\mathbf{u}_{\text{ff}}
$$

The complete control routine is summarized in Algorithm 1:

$$
\begin{array}{l}
\hline
\textbf{Algorithm 1: } \text{Inverse Kinematic Feedforward Control with Ellipsoid Gain Profile} \\
\hline
\textbf{Input: } \boldsymbol{q}_l = [v_{lx}, v_{ly}, \omega_l]^T, \; \tau_L, \tau_R, \; C_b, C_d, \; [\alpha_{\min}, \alpha_{\max}], \; r_x, r_y, \mathbf{o}, K_\theta, \alpha_{\text{ff}} \\
\textbf{Output: } \mathbf{u}_{\text{sp}} = [u_{\text{sp},L}, u_{\text{sp},R}]^T \text{ (Commanded dribbler wheel velocities in deg/s)} \\
\hline
\begin{array}{rl}
1: & r_b \leftarrow C_b / (2\pi), \quad \gamma \leftarrow C_b / C_d \\
2: & \textbf{for each } i \in \{L, R\} \textbf{ do} \\
3: & \quad \tau_{\text{norm},i} \leftarrow \frac{\tau_i - \tau_{i,\min}}{\tau_{i,\max} - \tau_{i,\min}} \times 100 \\
4: & \quad \alpha_i \leftarrow \alpha_{\min} + (\alpha_{\max} - \alpha_{\min})(\tau_{\text{norm},i} / 100) \\
5: & \quad [v_{bx,i}, v_{by,i}]^T \leftarrow C_b [\sin\alpha_i, \cos\alpha_i]^T \\
6: & \quad [\omega_{bx,i}, \omega_{by,i}]^T \leftarrow [v_{bx,i}, v_{by,i}]^T / r_b \\
7: & \quad [\omega_{\text{lin},x,i}, \omega_{\text{lin},y,i}]^T \leftarrow \gamma \left[v_{lx}/(\omega_{bx,i} + \epsilon), \; v_{ly}/(\omega_{by,i} + \epsilon)\right]^T \\
8: & \textbf{end for} \\
9: & [\omega_{\text{ang},L}, \omega_{\text{ang},R}]^T \leftarrow \gamma [-\omega_l, \; \omega_l]^T \\
10: & \psi \leftarrow \text{NormalizeAngle}\!\left(\operatorname{atan2}(v_{ly}, v_{lx} + \epsilon) - \pi / 2\right) \\
11: & g_x \leftarrow o_x + r_x \sin\psi, \quad g_y \leftarrow o_y + r_y \cos\psi \\
12: & K_{\text{lin}} \leftarrow \sqrt{g_x^2 + g_y^2} \\
13: & \omega_{\text{ff,lin},L} \leftarrow K_{\text{lin}}(\omega_{\text{lin},y,L} + \omega_{\text{lin},x,L}), \quad \omega_{\text{ff,lin},R} \leftarrow K_{\text{lin}}(\omega_{\text{lin},y,R} - \omega_{\text{lin},x,R}) \\
14: & \omega_{\text{ff,ang},L} \leftarrow K_\theta \omega_{\text{ang},L}, \quad \omega_{\text{ff,ang},R} \leftarrow K_\theta \omega_{\text{ang},R} \\
15: & u_{\text{ff},L} \leftarrow \frac{180}{\pi}(\omega_{\text{ff,lin},L} + \omega_{\text{ff,ang},L}), \quad u_{\text{ff},R} \leftarrow -\frac{180}{\pi}(\omega_{\text{ff,lin},R} + \omega_{\text{ff,ang},R}) \\
16: & \mathbf{u}_{\text{fb}} \leftarrow \text{TPSPositionPID}(\tau_{\text{norm},L}, \tau_{\text{norm},R}, v_{lx}, v_{ly}) \\
17: & \mathbf{u}_{\text{sp}} \leftarrow (1 - \alpha_{\text{ff}})\mathbf{u}_{\text{fb}} + \alpha_{\text{ff}}[u_{\text{ff},L}, u_{\text{ff},R}]^T \\
18: & \text{ActuateDribblerMotors}(\mathbf{u}_{\text{sp}})
\end{array} \\
\hline
\end{array}
$$

## Result

<div align="center">
  <video autoplay loop muted playsinline width="160">
    <source src="../../assets/images/inv_kinematic_dribble.mp4" type="video/mp4" />
  </video>
  <br>
  <sub>Natural dribbling feedforward simulation result</sub>
</div>

[Back to Projects](./../projects.md)

[Back to Main](./../../README.md)
