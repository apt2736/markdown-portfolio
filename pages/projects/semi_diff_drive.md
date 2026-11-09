---
layout: default
---

# Differential Drive-like Motion on Omnidirectional Robot with 3rd-Order Bézier Curve Path Planning

## Introduction

In the RoboCup Middle Size League (MSL), the most popular wheel configuration is the 3-wheeled omnidirectional system.

<table align="center">
  <tr>
    <td align="center">
      <img alt="Tech United Eindhoven Robot" src="../../assets/images/tu_eindhoven_robot.jpeg" height="190" />
    </td>
    <td align="center">
      <img alt="Falcons Robot" src="../../assets/images/falcons_tu_bots.jpeg" height="190" />
    </td>
    <td align="center">
      <img alt="IRIS Robot" src="../../assets/images/iris_bots.jpg" height="190" />
    </td>
  </tr>
  <tr>
    <td colspan="3" align="center">
      <sub>Examples of 3-wheeled omnidirectional robots from RoboCup MSL teams (Tech United Eindhoven, Falcons, IRIS).</sub>
    </td>
  </tr>
</table>

The main advantage of this system is that it allows simultaneous translation in any direction and independent rotation. However, unconstrained omnidirectional motion makes ball handling harder during dribbling. When the chassis slides laterally, the ball must follow without rolling out of the dribbler mechanism. On robots with mechanical dribbler constraints, lateral ball slip often causes lost possession. Constraining the omnidirectional base to differential drive-like motion using 3rd-order Bézier curves keeps the ball centered on the dribbler wheels and minimizes lateral slip.

## How it Works

MSL robots operate on a 2D plane, where linear velocity consists of two orthogonal components. Let $\mathbf{v}_l$ denote the linear velocity vector in the robot's local body frame:

$$
\mathbf{v}_l = \begin{bmatrix} v_{lx} \\ v_{ly} \end{bmatrix}
$$

Including angular velocity $\omega_l$ around the vertical $z$-axis, the body velocity state vector is:

$$
\boldsymbol{q}_l = \begin{bmatrix} v_{lx} \\ v_{ly} \\ \omega_l \end{bmatrix}
$$

To emulate differential drive motion, we set the lateral body velocity $v_{lx} = 0$, restricting linear translation to the local $y$-axis while allowing rotation about $z$:

$$
\boldsymbol{q}_l' = \begin{bmatrix} 0 \\ v_{ly} \\ \omega_l \end{bmatrix} = \begin{bmatrix} 0 \\ v_l \\ \omega_l \end{bmatrix}
$$

Let $\mathbf{p}_T$ be the target pose and $\mathbf{p}_O$ be the initial robot pose in the global coordinate frame:

$$
\mathbf{p}_T = \begin{bmatrix} x_T \\ y_T \\ \theta_T \end{bmatrix} \hspace{1cm} \mathbf{p}_O = \begin{bmatrix} x_O \\ y_O \\ \theta_O \end{bmatrix}
$$

The Euclidean distance from the robot to the target position is:

$$
d_t = \sqrt{\left(x_T - x_O\right)^2 + \left(y_T - y_O\right)^2}
$$

Because omnidirectional kinematics differ from nonholonomic differential drive kinematics, standard differential wheel equations cannot be applied directly. Instead, a cubic Bézier curve generates smooth waypoints that steer the robot along forward-facing arcs.

<div align="center">
  <img alt="3rd-Order Bezier Curve" src="../../assets/images/bezier_curve.png" height="200" />
  <br>
  <sub>3rd-Order Bezier Curve</sub>
</div>

A 3rd-order Bézier curve is defined as:

$$
\mathbf{B}_3(t) = (1 - t)^3 P_0 + 3t(1 - t)^2 P_1 + 3t^2(1 - t) P_2 + t^3 P_3
$$

where $P_0$ is the origin point, $P_3$ is the target point, and $P_1$ and $P_2$ are the intermediate control points. Let $d_q$ be the quarter distance from origin to target:

$$
d_q = \frac{d_t}{4}
$$

The control points $P_1$ and $P_2$ are generated as:

$$
P_1 = \begin{bmatrix} x_{P_1} \\ y_{P_1} \end{bmatrix} = \begin{bmatrix} -\dfrac{d_q}{\sqrt{1 + \tan^2(\theta_O)}} \\ \rule{0pt}{1.5em} (x_{P_1} - x_O)\tan(\theta_O) \end{bmatrix} + \begin{bmatrix} x_O \\ y_O \end{bmatrix}
$$

$$
P_2 = \begin{bmatrix} x_{P_2} \\ y_{P_2} \end{bmatrix} = \begin{bmatrix} -\dfrac{d_q}{\sqrt{1 + \tan^2(\theta_T)}} \\ \rule{0pt}{1.5em} (x_{P_2} - x_T)\tan(\theta_T) \end{bmatrix} + \begin{bmatrix} x_T \\ y_T \end{bmatrix}
$$

After computing the control points, De Casteljau's algorithm interpolates waypoints along the curve. To follow the interpolated waypoints, each consecutive waypoint pair is converted into linear and angular velocity commands:

$$
\mathbf{F}(x_m, y_m, x_n, y_n) = \begin{bmatrix} v_l \\ \omega_l \end{bmatrix} = \begin{bmatrix} \cos(\theta_R(t)) & \sin(\theta_R(t)) & 0 \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} v_{gx} \\ v_{gy} \\ \omega_g \end{bmatrix}
$$

$$
\begin{bmatrix} v_{gx} \\ v_{gy} \end{bmatrix} = d_{mn} \begin{bmatrix} \cos(\theta_{mn}) \\ \sin(\theta_{mn}) \end{bmatrix}
$$

$$
d_{mn} = \sqrt{(x_m - x_n)^2 + (y_m - y_n)^2}, \qquad \theta_{mn} = \arctan\left(\frac{y_m - y_n}{x_m - x_n}\right)
$$

where $(x_n, y_n)$ is the current waypoint, $(x_m, y_m)$ is the next waypoint, and $\theta_R(t)$ is the robot heading at time $t$, all expressed in the global coordinate frame. The resulting velocities form the commanded body velocity vector $\boldsymbol{q}_l'$.

For $180^\circ$ turns, the robot pivots around the ball rather than its own center. The chassis translates along its local $x$-axis while rotating about $z$, holding $v_{ly} = 0$ to maintain a constant radius to the ball:

$$
l_a = \omega_l r_b
$$

where $l_a$ is the linear arc velocity produced during the pivot and $r_b$ is the distance from the robot's rotation center to the ball center. The resulting body velocity vector is:

$$
\boldsymbol{q}_l = \begin{bmatrix} v_{lx} \\ v_{ly} \\ \omega_l \end{bmatrix} = \begin{bmatrix} l_a \\ 0 \\ \rule{0pt}{1.3em}\dfrac{l_a}{r_b} \end{bmatrix} = l_a \begin{bmatrix} 1 \\ 0 \\ \rule{0pt}{1.3em}\dfrac{1}{r_b} \end{bmatrix}
$$

After the velocity command vector is calculated, it is passed to the 3-wheeled omnidirectional robot inverse kinematics model:

<div align="center">
  <img alt="3-wheeled omnidirectional robot configuration" src="../../assets/images/Omni_3_4.png" height="220" />
  <br>
  <sub>3-wheeled omnidirectional robot configuration</sub>
</div>

$$
\begin{bmatrix} \omega_{w1} \\ \omega_{w2} \\ \omega_{w3} \end{bmatrix} = \dfrac{60}{2\pi r_w} \begin{bmatrix} \cos(q_1) & \sin(q_1) & 1 \\ \cos(q_2) & \sin(q_2) & 1 \\ \cos(q_3) & \sin(q_3) & 1 \end{bmatrix} \begin{bmatrix} v_{lx} \\ v_{ly} \\ \rule{0pt}{1.5em}\dfrac{2\pi r_w}{60}\omega_l \end{bmatrix}
$$

where $\omega_{w1}, \omega_{w2}, \omega_{w3}$ are wheel speeds in RPM, $r_w$ is wheel radius, and $q_1, q_2, q_3$ are the mounting angles.

The complete motion control loop is summarized in Algorithm 1:

$$
\begin{array}{l}
\hline
\textbf{Algorithm 1: } \text{Differential Drive-like Motion with Bézier Curve Path Planning} \\
\hline
\textbf{Input: } \mathbf{p}_O = [x_O, y_O, \theta_O]^T, \; \mathbf{p}_T = [x_T, y_T, \theta_T]^T, \; r_w, \; r_b, \; q_1, q_2, q_3 \\
\textbf{Output: } [\omega_{w1}, \omega_{w2}, \omega_{w3}]^T \text{ (Commanded wheel angular velocities in RPM)} \\
\hline
\begin{array}{rl}
1: & d_t \leftarrow \sqrt{(x_T - x_O)^2 + (y_T - y_O)^2}, \quad d_q \leftarrow d_t / 4 \\
2: & P_0 \leftarrow [x_O, y_O]^T, \quad P_3 \leftarrow [x_T, y_T]^T \\
3: & \text{Compute control points } P_1, P_2 \text{ using } (\theta_O, \theta_T) \text{ and } d_q \\
4: & \mathcal{W} \leftarrow \text{DeCasteljau}(P_0, P_1, P_2, P_3) \quad \text{(interpolate waypoints along } \mathbf{B}_3(t)\text{)} \\
5: & \textbf{while } \text{robot has not reached target pose } \mathbf{p}_T \textbf{ do} \\
6: & \quad (x_n, y_n), (x_m, y_m) \leftarrow \text{GetNextWaypointPair}(\mathcal{W}) \\
7: & \quad \textbf{if } \text{robot requires } 180^\circ \text{ pivot turn } \textbf{then} \\
8: & \quad\quad l_a \leftarrow \omega_l \cdot r_b \\
9: & \quad\quad \boldsymbol{q}_l \leftarrow l_a \left[1, \; 0, \; 1/r_b\right]^T \\
10: & \quad \textbf{else} \\
11: & \quad\quad d_{mn} \leftarrow \sqrt{(x_n - x_m)^2 + (y_n - y_m)^2} \\
12: & \quad\quad \theta_{mn} \leftarrow \arctan\left(\frac{y_n - y_m}{x_n - x_m}\right) \\
13: & \quad\quad [v_{gx}, v_{gy}]^T \leftarrow d_{mn} [\cos\theta_{mn}, \sin\theta_{mn}]^T \\
14: & \quad\quad [v_l, \omega_l]^T \leftarrow \mathbf{F}(x_m, y_m, x_n, y_n, \theta_R(t)) \\
15: & \quad\quad \boldsymbol{q}_l \leftarrow [0, \; v_l, \; \omega_l]^T \\
16: & \quad \textbf{end if} \\
17: & \quad [\omega_{w1}, \omega_{w2}, \omega_{w3}]^T \leftarrow \text{InverseKinematics}(\boldsymbol{q}_l, r_w, q_1, q_2, q_3) \\
18: & \quad \text{ActuateMotors}(\omega_{w1}, \omega_{w2}, \omega_{w3}) \\
19: & \textbf{end while}
\end{array} \\
\hline
\end{array}
$$

## Result

<div align="center">
  <img alt="Differential Drive Motion" src="../../assets/images/semi_diff.gif" width="560" />
  <br>
  <sub>Differential drive-like motion simulation result</sub>
</div>

## Source

Coming Soon

[Back to projects page](./../projects.md)

[Back to main page](./../../README.md)
