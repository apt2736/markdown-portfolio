import os
import sys
import math
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tactical_canvas import SCALE, W, H, PitchPanel, ease, lerp

N_FRAMES = 44
OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../images"))

C_ATT = (14, 165, 233)    # Sky blue
C_AST = (16, 185, 129)    # Emerald
C_DEF = (99, 102, 241)    # Indigo
C_OPP = (239, 68, 68)     # Crimson
C_GK  = (168, 85, 247)    # Purple

def save_gif(frames, filename, fps=14):
    path = os.path.join(OUT_DIR, filename)
    pal_frames = [f.convert("P", palette=Image.Palette.ADAPTIVE, colors=256) for f in frames]
    pal_frames[0].save(
        path,
        save_all=True,
        append_images=pal_frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True
    )
    print(f"Saved {path} ({len(frames)} frames)")

def make_attacker_set_piece():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        if t < 0.45:
            st1 = "Phase 1: Assist delivers forward pass (Pass = 1)"
            sc1 = (245, 158, 11)
        else:
            st1 = "Phase 2: Scoring unlocked! Turns to open corner and shoots"
            sc1 = (16, 185, 129)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(9.0, 22.8),
                        title="Home Restart: Receive & Shoot", status_text=st1, status_color=sc1)

        ast_pos = (3.0, 12.5)
        att_pos = (7.2, 16.0)
        opp_pos = (5.3, 18.2)
        gk_pos  = (8.0, 21.6)

        if t < 0.42:
            tp = ease(t / 0.42)
            bx = lerp(ast_pos[0] + 0.4, att_pos[0] - 0.3, tp)
            by = lerp(ast_pos[1] + 0.3, att_pos[1] - 0.3, tp)
            att_ang = math.degrees(math.atan2(ast_pos[1] - att_pos[1], ast_pos[0] - att_pos[0]))
            p1.draw_arrow(ast_pos, att_pos, color=(250, 204, 21), dashed=True)
        elif t < 0.62:
            tp = ease((t - 0.42) / 0.20)
            ang0 = math.degrees(math.atan2(ast_pos[1] - att_pos[1], ast_pos[0] - att_pos[0]))
            ang1 = math.degrees(math.atan2(22.0 - att_pos[1], 5.6 - att_pos[0]))
            att_ang = lerp(ang0, ang1, tp)
            rad = math.radians(att_ang)
            bx = att_pos[0] + 0.55 * math.cos(rad)
            by = att_pos[1] + 0.55 * math.sin(rad)
        else:
            tp = ease(min(1.0, (t - 0.62) / 0.28))
            att_ang = math.degrees(math.atan2(22.0 - att_pos[1], 5.6 - att_pos[0]))
            bx = lerp(att_pos[0], 5.6, tp)
            by = lerp(att_pos[1], 22.1, tp)
            p1.draw_arrow(att_pos, (5.6, 22.0), color=(56, 189, 248), dashed=True)

        p1.draw_robot(ast_pos[0], ast_pos[1], 38, "AST", C_AST)
        p1.draw_robot(opp_pos[0], opp_pos[1], -90, "OPP", C_OPP)
        p1.draw_robot(gk_pos[0], gk_pos[1], -90, "GK", C_GK)
        p1.draw_robot(att_pos[0], att_pos[1], att_ang, "ATT", C_ATT, highlight=True)
        p1.draw_ball(bx, by)

        if t < 0.52:
            st2 = "Stoppage: Holds 3.0 m standoff ring on ball-to-goal line"
            sc2 = (239, 68, 68)
        else:
            st2 = "Ball in Play: Breaks standoff to contest possession"
            sc2 = (14, 165, 233)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(6.0, 19.5),
                        title="Away Restart: Standoff & Press", status_text=st2, status_color=sc2)

        ball_start = (7.0, 14.5)
        p2.draw_dashed_line(ball_start, (7.0, 6.2), color=(148, 163, 184), width=1.5)

        if t < 0.52:
            tp = ease(t / 0.52)
            ax = lerp(4.8, 7.0, tp)
            ay = lerp(10.5, 11.5, tp)
            bx, by = ball_start
            ox, oy = (7.0, 15.3)
            p2.draw_dashed_circle(ball_start, 3.0, color=(248, 113, 113), width=2)
        else:
            tp = ease(min(1.0, (t - 0.52) / 0.38))
            ox = 7.0
            oy = lerp(15.3, 13.7, tp)
            bx = 7.0
            by = lerp(14.5, 13.0, tp)
            ax = 7.0
            ay = lerp(11.5, 12.2, tp)
            p2.draw_arrow((7.0, 11.5), (7.0, 12.6), color=C_ATT, dashed=False)

        p2.draw_robot(ox, oy, -90, "OPP", C_OPP)
        p2.draw_robot(ax, ay, 90, "ATT", C_ATT, highlight=True)
        p2.draw_ball(bx, by)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "attacker_set_piece.gif")

def make_attacker_has_ball():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        if t < 0.48:
            st1 = "Step 1: Shifts 60 cm inward & pivots past blocker"
            sc1 = (245, 158, 11)
        else:
            st1 = "Step 2: 3+ Robots -> Feeds Assist to unlock shooting"
            sc1 = (16, 185, 129)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(8.0, 21.0),
                        title="Steps 1-2: Clear Congestion & Pass", status_text=st1, status_color=sc1)

        opp_b = (2.1, 13.8)
        ast_p = (9.2, 15.5)

        if t < 0.48:
            tp = ease(t / 0.48)
            ax = lerp(1.0, 3.2, tp)
            ay = lerp(11.2, 12.5, tp)
            ang = lerp(90, 42, tp)
            rad = math.radians(ang)
            bx, by = ax + 0.55 * math.cos(rad), ay + 0.55 * math.sin(rad)
            p1.draw_arrow((1.0, 11.2), (3.2, 12.5), color=C_ATT, dashed=True)
        else:
            tp = ease(min(1.0, (t - 0.48) / 0.40))
            ax, ay = 3.2, 12.5
            ang = math.degrees(math.atan2(ast_p[1] - ay, ast_p[0] - ax))
            bx = lerp(ax + 0.5, ast_p[0] - 0.5, tp)
            by = lerp(ay + 0.25, ast_p[1] - 0.25, tp)
            p1.draw_arrow((ax, ay), ast_p, color=(250, 204, 21), dashed=True)

        p1.draw_robot(opp_b[0], opp_b[1], -90, "OPP", C_OPP)
        p1.draw_robot(ast_p[0], ast_p[1], -145, "AST", C_AST)
        p1.draw_robot(ax, ay, ang, "ATT", C_ATT, highlight=True)
        p1.draw_ball(bx, by)

        if t < 0.50:
            dist_d = lerp(0.0, 2.4, ease(t / 0.50))
            st2 = f"Step 3: Dribbles {dist_d:.1f} m / 2.5 m limit before reset"
            sc2 = (14, 165, 233)
        else:
            st2 = "Step 4: Vision detects empty side of goalpost -> Fires into open net"
            sc2 = (16, 185, 129)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(10.0, 22.8),
                        title="Steps 3-4: 2.5 m Dribble & Empty Goal Shot", status_text=st2, status_color=sc2)

        start_pos = (5.5, 13.5)
        end_drib  = (6.5, 15.7)
        opp_gk    = (8.0, 21.6)
        target_g  = (5.8, 22.0)

        p2.draw_dashed_circle(start_pos, 2.5, color=(56, 189, 248), width=1.6)

        if t < 0.50:
            tp = ease(t / 0.50)
            ax = lerp(start_pos[0], end_drib[0], tp)
            ay = lerp(start_pos[1], end_drib[1], tp)
            ang = 68
            rad = math.radians(ang)
            bx, by = ax + 0.55 * math.cos(rad), ay + 0.55 * math.sin(rad)
            p2.draw_arrow(start_pos, (ax, ay), color=C_ATT, dashed=False)
        else:
            tp = ease(min(1.0, (t - 0.50) / 0.38))
            ax, ay = end_drib
            ang = math.degrees(math.atan2(target_g[1] - ay, target_g[0] - ax))
            bx = lerp(ax - 0.1, target_g[0], tp)
            by = lerp(ay + 0.55, target_g[1], tp)

            # Highlight goalpost detection: blocked side vs empty side of the goalpost
            p2.draw_line((7.1, 22.0), (9.0, 22.0), color=(239, 68, 68), width=4.0)
            p2.draw_line((5.0, 22.0), (6.9, 22.0), color=(34, 197, 94), width=4.0)
            p2.draw_arrow((ax, ay), target_g, color=(250, 204, 21), dashed=True)

        p2.draw_robot(opp_gk[0], opp_gk[1], -90, "OPP", C_OPP)
        p2.draw_robot(ax, ay, ang, "ATT", C_ATT, highlight=True)
        p2.draw_ball(bx, by)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "attacker_has_ball.gif")

def make_attacker_off_ball():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        ast_p = (4.2, 11.0)
        opp_p = (5.4, 13.5)

        if t < 0.55:
            tp = ease(t / 0.55)
            ax = lerp(6.3, 9.2, tp)
            ay = lerp(15.6, 14.5, tp)
            bx, by = ast_p[0] + 0.35, ast_p[1] + 0.45
            p1_arrow = lambda: draw_p1_arrow_move()
        else:
            tp = ease(min(1.0, (t - 0.55) / 0.35))
            ax, ay = 9.2, 14.5
            bx = lerp(ast_p[0] + 0.4, ax - 0.4, tp)
            by = lerp(ast_p[1] + 0.3, ay - 0.3, tp)

        # Dynamic cone checking LoS from Assist (ast_p) to Attacker (ax, ay)
        v_att = (ax - ast_p[0], ay - ast_p[1])
        v_opp = (opp_p[0] - ast_p[0], opp_p[1] - ast_p[1])
        ang_att = math.atan2(v_att[1], v_att[0])
        ang_opp = math.atan2(v_opp[1], v_opp[0])
        diff = abs((ang_opp - ang_att + math.pi) % (2 * math.pi) - math.pi)
        ha = math.radians(14)
        dist_att = math.hypot(v_att[0], v_att[1])

        is_blocked = (diff < ha)
        cone_color = (248, 113, 113) if is_blocked else (52, 211, 153)

        if is_blocked:
            st1 = "Pass Needed: Assist passing cone to Attacker blocked by Opponent"
            sc1 = (239, 68, 68)
        else:
            st1 = "Lane Clear: Attacker evades cone shadow -> Assist delivers pass"
            sc1 = (16, 185, 129)

        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(8.0, 20.5),
                        title="Before Pass: Evading Cone Shadow", status_text=st1, status_color=sc1)

        # Cone originates on Assist (apex at ast_p directed towards Attacker (ax, ay))
        p1.draw_cone(ast_p, (ax, ay), half_angle_deg=14, length_m=dist_att + 0.6, outline_color=cone_color)

        if t < 0.55:
            p1.draw_arrow((6.3, 15.6), (9.2, 14.5), color=C_ATT, dashed=True)
        else:
            p1.draw_arrow(ast_p, (ax, ay), color=(52, 211, 153), dashed=True)

        ast_ang = math.degrees(ang_att)
        att_ang = math.degrees(math.atan2(ast_p[1] - ay, ast_p[0] - ax))
        opp_ang = math.degrees(math.atan2(ast_p[1] - opp_p[1], ast_p[0] - opp_p[0]))

        p1.draw_robot(ast_p[0], ast_p[1], ast_ang, "AST", C_AST)
        p1.draw_robot(opp_p[0], opp_p[1], opp_ang, "OPP", C_OPP)
        p1.draw_robot(ax, ay, att_ang, "ATT", C_ATT, highlight=True)
        p1.draw_ball(bx, by)

        st2 = "Scoring Unlocked: Non-dribblers orient yaw to ball carrier"
        sc2 = (14, 165, 233)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(9.0, 22.0),
                        title="After Pass: Opposite Flank Advance", status_text=st2, status_color=sc2)

        tp = ease(min(1.0, t / 0.85))
        ast_x, ast_y = 3.6, lerp(11.8, 16.5, tp)
        att_x, att_y = 10.4, lerp(12.2, 18.2, tp)
        opp1_x, opp1_y = lerp(6.2, 4.8, tp), 17.5
        opp2_x, opp2_y = lerp(7.8, 8.4, tp), 18.5

        # All non-dribbling robots orient their yaw to the dribbler (ast_x, ast_y)
        att_r_ang = math.degrees(math.atan2(ast_y - att_y, ast_x - att_x))
        opp1_ang = math.degrees(math.atan2(ast_y - opp1_y, ast_x - opp1_x))
        opp2_ang = math.degrees(math.atan2(ast_y - opp2_y, ast_x - opp2_x))

        p2.draw_arrow((3.6, 11.8), (3.6, 16.8), color=C_AST, dashed=True)
        p2.draw_arrow((10.4, 12.2), (10.4, 18.5), color=C_ATT, dashed=True)
        p2.draw_dashed_line((ast_x, ast_y), (att_x, att_y), color=(250, 204, 21), width=1.5)

        # Dribbler faces forward; non-dribblers face the dribbler
        p2.draw_robot(ast_x, ast_y, 90, "AST", C_AST)
        p2.draw_robot(opp1_x, opp1_y, opp1_ang, "OPP", C_OPP)
        p2.draw_robot(opp2_x, opp2_y, opp2_ang, "OPP", C_OPP)
        p2.draw_robot(att_x, att_y, att_r_ang, "ATT", C_ATT, highlight=True)
        p2.draw_ball(ast_x, ast_y + 0.55)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "attacker_off_ball.gif")

def make_attacker_pressing_pursuit():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        if t < 0.65:
            st1 = "Back Turned: Orbits at 2.3 m radius to avoid rear foul"
            sc1 = (245, 158, 11)
        else:
            st1 = "Facing Ball: Closes in from front for clean tackle"
            sc1 = (16, 185, 129)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(9.0, 21.0),
                        title="Opponent Has Ball: 2.3 m Orbit Tackle", status_text=st1, status_color=sc1)

        ox, oy = 7.0, 14.5
        bx, by = 7.0, 15.1
        p1.draw_dashed_circle((ox, oy), 2.3, color=(251, 191, 36), width=1.8)

        if t < 0.65:
            tp = ease(t / 0.65)
            orbit_deg = lerp(-85, 85, tp)
            rad = math.radians(orbit_deg)
            ax = ox + 2.3 * math.cos(rad)
            ay = oy + 2.3 * math.sin(rad)
            att_ang = math.degrees(math.atan2(by - ay, bx - ax))
            p1.draw_arc_segment((ox, oy), 2.3, -85, orbit_deg, color=C_ATT, width=2.8, dashed=False)
        else:
            tp = ease(min(1.0, (t - 0.65) / 0.28))
            ax = lerp(ox + 2.3 * math.cos(math.radians(85)), 7.0, tp)
            ay = lerp(oy + 2.3 * math.sin(math.radians(85)), 15.75, tp)
            att_ang = -90
            p1.draw_arrow((7.0, 16.8), (7.0, 15.6), color=(52, 211, 153), dashed=False)

        p1.draw_robot(ox, oy, 90, "OPP", C_OPP)
        p1.draw_ball(bx, by)
        p1.draw_robot(ax, ay, att_ang, "ATT", C_ATT, highlight=True)

        if t < 0.62:
            st2 = "Near Touchline: Loops wide to face inward toward field"
            sc2 = (245, 158, 11)
        else:
            st2 = "Facing Inward: Gathers ball safely without out-of-bounds"
            sc2 = (14, 165, 233)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(9.0, 21.0),
                        title="Loose Ball: Boundary-Safe Pursuit", status_text=st2, status_color=sc2)

        ball_l = (12.8, 15.0)
        p2.draw_dashed_line((8.5, 12.5), (13.8, 15.6), color=(248, 113, 113), width=1.6)

        pts_curve = [
            (8.5, 12.2),
            (11.8, 12.5),
            (13.6, 13.8),
            (13.55, 15.3),
            (12.2, 15.0)
        ]
        if t < 0.68:
            tp = ease(t / 0.68)
            u = tp * 3.0
            idx = min(2, int(u))
            frac = u - idx
            p_curr = (lerp(pts_curve[idx][0], pts_curve[idx+1][0], frac),
                      lerp(pts_curve[idx][1], pts_curve[idx+1][1], frac))
            ax, ay = p_curr
            bx2, by2 = ball_l
            att_ang = math.degrees(math.atan2(by2 - ay, bx2 - ax))
        else:
            tp = ease(min(1.0, (t - 0.68) / 0.25))
            ax = lerp(13.55, 11.4, tp)
            ay = lerp(15.2, 15.0, tp)
            att_ang = 180
            bx2, by2 = ax - 0.55, ay

        for k in range(3):
            p2.draw_dashed_line(pts_curve[k], pts_curve[k+1], color=(52, 211, 153), width=2.0)

        p2.draw_ball(bx2, by2)
        p2.draw_robot(ax, ay, att_ang, "ATT", C_ATT, highlight=True)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "attacker_pressing_pursuit.gif")

if __name__ == "__main__":
    make_attacker_set_piece()
    make_attacker_has_ball()
    make_attacker_off_ball()
    make_attacker_pressing_pursuit()
