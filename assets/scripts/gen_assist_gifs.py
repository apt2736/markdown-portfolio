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

def make_assist_set_piece():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        if t < 0.50:
            st1 = "Prep: Circles ball to align passing line to Attacker"
            sc1 = (245, 158, 11)
        else:
            st1 = "Start Signal: Feeds opening pass & pauses briefly"
            sc1 = (16, 185, 129)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(7.0, 20.0),
                        title="Home Restart: Align & Deliver Pass", status_text=st1, status_color=sc1)

        ball_0 = (3.5, 12.0)
        att_p  = (8.5, 16.0)
        line_ang = math.atan2(att_p[1] - ball_0[1], att_p[0] - ball_0[0])
        p1.draw_dashed_line((ball_0[0] - 1.2*math.cos(line_ang), ball_0[1] - 1.2*math.sin(line_ang)),
                            att_p, color=(148, 163, 184), width=1.5)

        if t < 0.50:
            tp = ease(t / 0.50)
            a_start = math.radians(130)
            a_end   = line_ang + math.pi
            a_cur   = lerp(a_start, a_end, tp)
            ast_x = ball_0[0] + 0.95 * math.cos(a_cur)
            ast_y = ball_0[1] + 0.95 * math.sin(a_cur)
            ast_ang = math.degrees(math.atan2(ball_0[1] - ast_y, ball_0[0] - ast_x))
            bx, by = ball_0
            p1.draw_arc_segment(ball_0, 0.95, 130, math.degrees(a_cur), color=C_AST, width=2.2, dashed=False)
        else:
            tp = ease(min(1.0, (t - 0.50) / 0.38))
            a_end = line_ang + math.pi
            ast_x = ball_0[0] + 0.75 * math.cos(a_end)
            ast_y = ball_0[1] + 0.75 * math.sin(a_end)
            ast_ang = math.degrees(line_ang)
            bx = lerp(ball_0[0], att_p[0] - 0.5, tp)
            by = lerp(ball_0[1], att_p[1] - 0.4, tp)
            p1.draw_arrow(ball_0, att_p, color=(250, 204, 21), dashed=True)

        p1.draw_robot(att_p[0], att_p[1], math.degrees(line_ang) + 180, "ATT", C_ATT)
        p1.draw_robot(ast_x, ast_y, ast_ang, "AST", C_AST, highlight=True)
        p1.draw_ball(bx, by)

        st2 = "Stoppage: Guards 3.8 m secondary arc to cut off wing passes"
        sc2 = (16, 185, 129)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(6.0, 19.5),
                        title="Away Restart: Secondary Wing Arc", status_text=st2, status_color=sc2)

        b_away = (6.5, 14.5)
        opp_w  = (11.2, 12.2)
        p2.draw_dashed_circle(b_away, 3.0, color=(248, 113, 113), width=1.6)
        p2.draw_arc_segment(b_away, 3.8, -95, -15, color=C_AST, width=2.2, dashed=True)
        p2.draw_dashed_line(b_away, (7.0, 6.2), color=(148, 163, 184), width=1.4)
        p2.draw_dashed_line(b_away, opp_w, color=(252, 165, 165), width=1.6)

        tp = ease(min(1.0, t / 0.70))
        arc_a = math.radians(lerp(-78, -32, tp))
        ast_x2 = b_away[0] + 3.8 * math.cos(arc_a)
        ast_y2 = b_away[1] + 3.8 * math.sin(arc_a)
        ast_ang2 = math.degrees(math.atan2(b_away[1] - ast_y2, b_away[0] - ast_x2))

        p2.draw_robot(6.5, 15.3, -90, "OPP", C_OPP)
        p2.draw_robot(opp_w[0], opp_w[1], 145, "OPP2", C_OPP)
        p2.draw_robot(6.6, 11.5, 90, "ATT", C_ATT)
        p2.draw_robot(ast_x2, ast_y2, ast_ang2, "AST", C_AST, highlight=True)
        p2.draw_ball(*b_away)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "assist_set_piece.gif")

def make_assist_has_ball():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        if t < 0.50:
            st1 = "Pass Needed & Lane Clear: Feeds open Attacker"
            sc1 = (16, 185, 129)
        else:
            st1 = "Attacker Marked: Dribbles into attacking half & shoots"
            sc1 = (14, 165, 233)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(9.0, 22.8),
                        title="Full Squad (3+ Robots): Pass vs Shoot", status_text=st1, status_color=sc1)

        if t < 0.50:
            tp = ease(t / 0.45)
            ast_p = (4.2, 12.5)
            att_p = (9.2, 16.5)
            opp_p = (5.0, 17.5)
            ang = math.degrees(math.atan2(att_p[1] - ast_p[1], att_p[0] - ast_p[0]))
            bx = lerp(ast_p[0] + 0.4, att_p[0] - 0.4, tp)
            by = lerp(ast_p[1] + 0.3, att_p[1] - 0.3, tp)
            p1.draw_arrow(ast_p, att_p, color=(250, 204, 21), dashed=True)
        else:
            tp = ease(min(1.0, (t - 0.50) / 0.42))
            att_p = (9.8, 16.5)
            opp_p = (8.8, 15.8)
            ast_x = lerp(4.2, 5.2, min(1.0, tp * 1.6))
            ast_y = lerp(12.5, 16.2, min(1.0, tp * 1.6))
            ang = math.degrees(math.atan2(22.0 - ast_y, 6.2 - ast_x))
            if tp < 0.55:
                rad = math.radians(ang)
                bx, by = ast_x + 0.55*math.cos(rad), ast_y + 0.55*math.sin(rad)
            else:
                st = (tp - 0.55) / 0.45
                bx = lerp(5.2, 6.0, st)
                by = lerp(16.7, 22.0, st)
            p1.draw_dashed_line((4.2, 12.5), att_p, color=(248, 113, 113), width=1.6)
            p1.draw_arrow((ast_x, ast_y), (6.0, 22.0), color=(56, 189, 248), dashed=True)

        p1.draw_robot(7.8, 21.6, -90, "GK", C_GK)
        p1.draw_robot(opp_p[0], opp_p[1], -90, "OPP", C_OPP)
        p1.draw_robot(att_p[0], att_p[1], -135, "ATT", C_ATT)
        if t < 0.50:
            p1.draw_robot(ast_p[0], ast_p[1], ang, "AST", C_AST, highlight=True)
        else:
            p1.draw_robot(ast_x, ast_y, ang, "AST", C_AST, highlight=True)
        p1.draw_ball(bx, by)

        st2 = "Filters out home GK -> Calculates distance-scaled kick P_kick"
        sc2 = (16, 185, 129)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(-0.5, 14.5),
                        title="2-Robot Squad: Scaled Pass & GK Filter", status_text=st2, status_color=sc2)

        ast_2 = (6.0, 2.8)
        gk_home = (6.8, 1.2)
        att_2 = (9.2, 10.2)
        p2.draw_dashed_circle(ast_2, 2.0, color=(148, 163, 184), width=1.6)

        tp = ease(min(1.0, max(0.0, (t - 0.15) / 0.72)))
        ang2 = math.degrees(math.atan2(att_2[1] - ast_2[1], att_2[0] - ast_2[0]))
        bx2 = lerp(ast_2[0] + 0.25, att_2[0] - 0.3, tp)
        by2 = lerp(ast_2[1] + 0.5, att_2[1] - 0.4, tp)
        p2.draw_arrow(ast_2, att_2, color=(250, 204, 21), dashed=True)

        p2.draw_robot(gk_home[0], gk_home[1], 90, "GK", C_GK)
        p2.draw_robot(att_2[0], att_2[1], ang2 + 180, "ATT", C_ATT)
        p2.draw_robot(ast_2[0], ast_2[1], ang2, "AST", C_AST, highlight=True)
        p2.draw_ball(bx2, by2)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "assist_has_ball.gif")

def make_assist_off_ball():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        att_p = (9.5, 14.2)
        opp_p = (7.2, 14.0)

        if t < 0.55:
            tp = ease(t / 0.55)
            ast_x = lerp(5.0, 5.8, tp)
            ast_y = lerp(13.8, 16.5, tp)
            bx, by = att_p[0] - 0.5, att_p[1]
        else:
            tp = ease(min(1.0, (t - 0.55) / 0.35))
            ast_x, ast_y = 5.8, 16.5
            bx = lerp(att_p[0] - 0.4, ast_x + 0.4, tp)
            by = lerp(att_p[1] + 0.2, ast_y - 0.2, tp)

        # Dynamic cone from Attacker att_p tracking Assist (ast_x, ast_y)
        v_ast = (ast_x - att_p[0], ast_y - att_p[1])
        v_opp = (opp_p[0] - att_p[0], opp_p[1] - att_p[1])
        ang_ast = math.atan2(v_ast[1], v_ast[0])
        ang_opp = math.atan2(v_opp[1], v_opp[0])
        diff = abs((ang_opp - ang_ast + math.pi) % (2 * math.pi) - math.pi)
        ha = math.radians(14)
        dist_ast = math.hypot(v_ast[0], v_ast[1])

        is_blocked = (diff < ha)
        cone_color = (248, 113, 113) if is_blocked else (52, 211, 153)

        if is_blocked:
            st1 = "Pass Needed: Passing cone from Attacker blocked by Opponent"
            sc1 = (239, 68, 68)
        else:
            st1 = "Lane Clear: Assist shifts out of shadow -> Attacker delivers pass"
            sc1 = (16, 185, 129)

        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(8.0, 20.5),
                        title="Before Pass: Opening 3 m Outlet", status_text=st1, status_color=sc1)

        # Cone originates on Attacker (apex at att_p directed to Assist (ast_x, ast_y))
        p1.draw_cone(att_p, (ast_x, ast_y), half_angle_deg=14, length_m=dist_ast + 0.6, outline_color=cone_color)

        if t < 0.55:
            p1.draw_arrow((5.0, 13.8), (5.8, 16.5), color=C_AST, dashed=True)
        else:
            p1.draw_arrow(att_p, (ast_x, ast_y), color=(52, 211, 153), dashed=True)

        ast_ang = math.degrees(math.atan2(att_p[1] - ast_y, att_p[0] - ast_x))
        att_ang = math.degrees(ang_ast)
        opp_ang = math.degrees(math.atan2(att_p[1] - opp_p[1], att_p[0] - opp_p[0]))

        p1.draw_robot(opp_p[0], opp_p[1], opp_ang, "OPP", C_OPP)
        p1.draw_robot(att_p[0], att_p[1], att_ang, "ATT", C_ATT)
        p1.draw_robot(ast_x, ast_y, ast_ang, "AST", C_AST, highlight=True)
        p1.draw_ball(bx, by)

        # Right Side: Assist passes to Attacker in midfield, then Attacker moves forward and Assist covers
        ast_mid = (4.5, 10.5)
        att_mid = (8.5, 11.5)

        if t < 0.38:
            tp_pass = ease(t / 0.38)
            st2 = "Pass Complete: Assist passes to Attacker in midfield to unlock scoring"
            sc2 = (250, 204, 21)
            ast_x2, ast_y2 = ast_mid
            att_x2, att_y2 = att_mid
            bx2 = lerp(ast_mid[0] + 0.4, att_mid[0] - 0.4, tp_pass)
            by2 = lerp(ast_mid[1] + 0.1, att_mid[1] - 0.1, tp_pass)
            ast_ang2 = math.degrees(math.atan2(att_mid[1] - ast_mid[1], att_mid[0] - ast_mid[0]))
            att_ang2 = math.degrees(math.atan2(ast_mid[1] - att_mid[1], ast_mid[0] - att_mid[0]))
        else:
            tp_fwd = ease(min(1.0, (t - 0.38) / 0.58))
            st2 = "Scoring Unlocked: Attacker drives forward | Assist covers at y = 5.5 m"
            sc2 = (16, 185, 129)
            att_x2 = lerp(att_mid[0], 9.2, tp_fwd)
            att_y2 = lerp(att_mid[1], 17.5, tp_fwd)
            bx2 = att_x2
            by2 = att_y2 + 0.55
            att_ang2 = 82

            target_cover_x = 7.0 + (5.5 / by2) * (bx2 - 7.0)
            ast_x2 = lerp(ast_mid[0], target_cover_x, tp_fwd)
            ast_y2 = lerp(ast_mid[1], 5.5, tp_fwd)
            ast_ang2 = math.degrees(math.atan2(by2 - ast_y2, bx2 - ast_x2))

        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(0.0, 19.5),
                        title="After Pass: Midfield Feed & Defensive Cover", status_text=st2, status_color=sc2)

        # Defensive quarter-line at y = 5.5 m
        p2.draw_dashed_line((0.5, 5.5), (13.5, 5.5), color=(148, 163, 184), width=1.6)

        if t < 0.38:
            p2.draw_arrow(ast_mid, att_mid, color=(250, 204, 21), dashed=True)
        else:
            # Ball-to-goal tracking line
            p2.draw_dashed_line((bx2, by2), (7.0, 0.0), color=(250, 204, 21), width=1.5)
            p2.draw_arrow(att_mid, (9.2, 17.5), color=C_ATT, dashed=True)
            p2.draw_arrow(ast_mid, (target_cover_x, 5.5), color=C_AST, dashed=True)

        # No opponent robot on right side per request
        p2.draw_robot(att_x2, att_y2, att_ang2, "ATT", C_ATT)
        p2.draw_robot(ast_x2, ast_y2, ast_ang2, "AST", C_AST, highlight=True)
        p2.draw_ball(bx2, by2)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "assist_off_ball.gif")

def make_assist_containment_intercept():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        st1 = "Opponent Ball: ATT presses | AST holds 3 m barrier on goal line"
        sc1 = (16, 185, 129)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(4.0, 18.0),
                        title="Opponent Has Ball: 3 m Barrier", status_text=st1, status_color=sc1)

        tp = ease(min(1.0, t / 0.85))
        ox = lerp(9.5, 5.2, tp)
        oy = lerp(14.5, 12.5, tp)
        bx, by = ox, oy - 0.55

        dx, dy = 7.0 - bx, 0.0 - by
        dist_bg = math.hypot(dx, dy)
        ux, uy = dx / dist_bg, dy / dist_bg
        ast_x = bx + 3.0 * ux
        ast_y = by + 3.0 * uy

        att_x = lerp(10.8, 5.8, tp)
        att_y = lerp(15.2, 13.3, tp)

        p1.draw_dashed_line((bx, by), (7.0, 4.2), color=(250, 204, 21), width=1.6)
        p1.draw_dashed_circle((bx, by), 3.0, color=C_AST, width=1.6)

        p1.draw_robot(ox, oy, -110, "OPP", C_OPP)
        p1.draw_robot(att_x, att_y, -135, "ATT", C_ATT)
        p1.draw_robot(ast_x, ast_y, math.degrees(math.atan2(-uy, -ux)), "AST", C_AST, highlight=True)
        p1.draw_ball(bx, by)

        st2 = "Loose Ball: Drives to lead point ahead on trajectory: p_intercept"
        sc2 = (14, 165, 233)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(4.0, 18.0),
                        title="Loose Ball: Predictive Interception", status_text=st2, status_color=sc2)

        b_start = (2.2, 15.2)
        b_end   = (9.5, 8.5)
        ast_0   = (10.8, 14.0)

        p2.draw_dashed_line(b_start, b_end, color=(250, 204, 21), width=1.8)
        p2.draw_dashed_line(ast_0, (4.5, 13.1), color=(248, 113, 113), width=1.5)

        tp2 = ease(min(1.0, t / 0.82))
        bx2 = lerp(b_start[0], b_end[0], tp2)
        by2 = lerp(b_start[1], b_end[1], tp2)

        lead_t = min(1.0, tp2 + 0.22)
        lx = lerp(b_start[0], b_end[0], lead_t)
        ly = lerp(b_start[1], b_end[1], lead_t)

        ast_x2 = lerp(ast_0[0], b_end[0] + 0.35, tp2)
        ast_y2 = lerp(ast_0[1], b_end[1] + 0.35, tp2)
        ast_ang2 = math.degrees(math.atan2(by2 - ast_y2, bx2 - ast_x2))

        if tp2 < 0.85:
            p2.draw_arrow((bx2, by2), (lx, ly), color=(52, 211, 153), width=2.5, dashed=False)
            p2.draw_arrow((ast_x2, ast_y2), (b_end[0], b_end[1]), color=C_AST, dashed=True)

        p2.draw_ball(bx2, by2)
        p2.draw_robot(ast_x2, ast_y2, ast_ang2, "AST", C_AST, highlight=True)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "assist_containment_intercept.gif")

if __name__ == "__main__":
    make_assist_set_piece()
    make_assist_has_ball()
    make_assist_off_ball()
    make_assist_containment_intercept()
