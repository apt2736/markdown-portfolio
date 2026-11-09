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

def make_defender_set_piece():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        osc = 0.5 - 0.5 * math.cos(2 * math.pi * t)

        st1 = "Ball > 6.4 m away: Tracks default R = 3.4 m arc centered on goal"
        sc1 = (99, 102, 241)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(-0.8, 12.0),
                        title="Far Restart (d >= 6.4 m): Default Arc", status_text=st1, status_color=sc1)

        bx1 = lerp(4.0, 10.0, osc)
        by1 = 8.5
        goal = (7.0, 0.0)
        ang1 = math.atan2(by1 - goal[1], bx1 - goal[0])
        R_def = 3.4
        dx1 = goal[0] + R_def * math.cos(ang1)
        dy1 = goal[1] + R_def * math.sin(ang1)

        p1.draw_arc_segment(goal, R_def, 25, 155, color=C_DEF, width=2.2, dashed=True)
        p1.draw_dashed_circle((bx1, by1), 3.0, color=(248, 113, 113), width=1.6)
        p1.draw_dashed_line((bx1, by1), goal, color=(250, 204, 21), width=1.6)

        p1.draw_robot(7.0, 0.4, 90, "GK", C_GK)
        p1.draw_robot(bx1, by1 + 0.7, -90, "OPP", C_OPP)
        p1.draw_robot(dx1, dy1, math.degrees(ang1), "DEF", C_DEF, highlight=True)
        p1.draw_ball(bx1, by1)

        st2 = "Ball < 6.4 m away: Contracts arc R = d_ball - 3.0 m outside box"
        sc2 = (245, 158, 11)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(-0.8, 12.0),
                        title="Close Restart: Contracted Guard Arc", status_text=st2, status_color=sc2)

        bx2, by2 = 5.4, 5.4
        d_bg = math.hypot(bx2 - goal[0], by2 - goal[1])
        R_contract = d_bg - 3.0
        ang2 = math.atan2(by2 - goal[1], bx2 - goal[0])

        tp2 = ease(min(1.0, t / 0.65))
        r_curr = lerp(3.4, R_contract, tp2)
        dx2 = goal[0] + r_curr * math.cos(ang2)
        dy2 = goal[1] + r_curr * math.sin(ang2)

        p2.draw_arc_segment(goal, 3.4, 30, 150, color=(148, 163, 184), width=1.5, dashed=True)
        p2.draw_arc_segment(goal, R_contract, 30, 150, color=(52, 211, 153), width=2.4, dashed=True)
        p2.draw_dashed_circle((bx2, by2), 3.0, color=(248, 113, 113), width=2.0)
        p2.draw_dashed_line((bx2, by2), goal, color=(250, 204, 21), width=1.6)

        p2.draw_robot(7.0, 0.4, 90, "GK", C_GK)
        p2.draw_robot(bx2 - 0.3, by2 + 0.7, -75, "OPP", C_OPP)
        p2.draw_robot(dx2, dy2, math.degrees(ang2), "DEF", C_DEF, highlight=True)
        p2.draw_ball(bx2, by2)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "defender_set_piece.gif")

def make_defender_shot_blocking():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        osc = 0.5 - 0.5 * math.cos(2 * math.pi * t)
        goal = (7.0, 0.0)
        y_def = 3.0

        st1 = "Slides along y = 3.0 m to intersect direct ball-to-goal ray"
        sc1 = (99, 102, 241)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(-0.8, 12.5),
                        title="StandBy: Collinear Shot Blocking", status_text=st1, status_color=sc1)

        bx1 = lerp(3.5, 10.5, osc)
        by1 = 9.5
        x_inter1 = bx1 + (y_def - by1) * (goal[0] - bx1) / (goal[1] - by1)
        x_def1 = max(3.25, min(10.75, x_inter1))

        p1.draw_dashed_line((2.5, y_def), (11.5, y_def), color=(148, 163, 184), width=1.6)
        p1.draw_dashed_line((bx1, by1), goal, color=(250, 204, 21), width=2.0)

        ang1 = math.degrees(math.atan2(by1 - y_def, bx1 - x_def1))
        p1.draw_robot(7.0, 0.4, 90, "GK", C_GK)
        p1.draw_robot(bx1, by1 + 0.65, -90, "OPP", C_OPP)
        p1.draw_robot(x_def1, y_def, ang1, "DEF", C_DEF, highlight=True)
        p1.draw_ball(bx1, by1)

        st2 = "Wide angle: Clamps x_def between penalty box edges [3.25, 10.75]"
        sc2 = (16, 185, 129)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(-0.8, 12.5),
                        title="Wide Threat: Box-Edge Clamping", status_text=st2, status_color=sc2)

        bx2 = lerp(0.8, 13.2, osc)
        by2 = 5.2
        x_raw2 = bx2 + (y_def - by2) * (goal[0] - bx2) / (goal[1] - by2)
        x_def2 = max(3.25, min(10.75, x_raw2))

        p2.draw_dashed_line((3.25, 2.25), (3.25, 4.2), color=(52, 211, 153), width=1.8)
        p2.draw_dashed_line((10.75, 2.25), (10.75, 4.2), color=(52, 211, 153), width=1.8)
        p2.draw_dashed_line((bx2, by2), goal, color=(250, 204, 21), width=1.6)

        ang2 = math.degrees(math.atan2(by2 - y_def, bx2 - x_def2))
        p2.draw_robot(7.0, 0.4, 90, "GK", C_GK)
        p2.draw_robot(bx2, by2 + 0.65, -90, "OPP", C_OPP)
        p2.draw_robot(x_def2, y_def, ang2, "DEF", C_DEF, highlight=True)
        p2.draw_ball(bx2, by2)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "defender_shot_blocking.gif")

def make_defender_has_ball():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        if t < 0.48:
            st1 = "Step 1: Escapes central goal mouth toward nearer flank"
            sc1 = (245, 158, 11)
        else:
            st1 = "Step 2: Corridor clear -> Passes forward to Attacker"
            sc1 = (16, 185, 129)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(-0.5, 14.5),
                        title="Steps 1-2: Flank Escape & Pass", status_text=st1, status_color=sc1)

        att_p = (3.8, 11.8)
        opp_p = (7.5, 7.5)

        if t < 0.48:
            tp = ease(t / 0.48)
            dx = lerp(6.2, 3.5, tp)
            dy = lerp(3.0, 4.2, tp)
            ang = lerp(155, 85, tp)
            rad = math.radians(ang)
            bx, by = dx + 0.55 * math.cos(rad), dy + 0.55 * math.sin(rad)
            p1.draw_arrow((6.2, 3.0), (3.5, 4.2), color=C_DEF, dashed=True)
        else:
            tp = ease(min(1.0, (t - 0.48) / 0.40))
            dx, dy = 3.5, 4.2
            ang = math.degrees(math.atan2(att_p[1] - dy, att_p[0] - dx))
            bx = lerp(dx + 0.1, att_p[0] - 0.1, tp)
            by = lerp(dy + 0.55, att_p[1] - 0.55, tp)
            p1.draw_arrow((dx, dy), att_p, color=(52, 211, 153), dashed=True)

        p1.draw_robot(7.0, 0.5, 90, "GK", C_GK)
        p1.draw_robot(opp_p[0], opp_p[1], -90, "OPP", C_OPP)
        p1.draw_robot(att_p[0], att_p[1], -90, "ATT", C_ATT)
        p1.draw_robot(dx, dy, ang, "DEF", C_DEF, highlight=True)
        p1.draw_ball(bx, by)

        if t < 0.52:
            dist_c = lerp(0.0, 2.5, ease(t / 0.52))
            st2 = f"Opponent near teammate: Flank carry ({dist_c:.1f} m / 2.5 m cap)"
            sc2 = (245, 158, 11)
        else:
            st2 = "Teammate Marked: Defender shoots directly toward opponent goalpost"
            sc2 = (14, 165, 233)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(-0.5, 14.5),
                        title="Step 3: Direct Shot toward Opponent Goal", status_text=st2, status_color=sc2)

        start_d = (8.8, 3.0)
        end_d   = (10.5, 4.8)
        # Friend and opponent positioned on the left side of the field
        att_m   = (3.8, 11.5)
        opp_m   = (4.2, 10.3)
        goal_opp = (7.0, 22.0)

        p2.draw_dashed_circle(start_d, 2.5, color=C_DEF, width=1.6)
        # Opponent closely marking teammate on the left side
        p2.draw_dashed_line(opp_m, att_m, color=(248, 113, 113), width=1.8)

        if t < 0.52:
            tp = ease(t / 0.52)
            dx2 = lerp(start_d[0], end_d[0], tp)
            dy2 = lerp(start_d[1], end_d[1], tp)
            ang2 = 48
            rad2 = math.radians(ang2)
            bx2, by2 = dx2 + 0.55 * math.cos(rad2), dy2 + 0.55 * math.sin(rad2)
            p2.draw_arrow(start_d, (dx2, dy2), color=C_DEF, dashed=False)
        else:
            tp = ease(min(1.0, (t - 0.52) / 0.38))
            dx2, dy2 = end_d
            ang2 = math.degrees(math.atan2(goal_opp[1] - dy2, goal_opp[0] - dx2))
            # Ray toward opponent goalpost (7.0, 22.0), crossing panel top at y = 14.5:
            x_exit = 8.53
            y_exit = 14.5
            bx2 = lerp(dx2, x_exit, tp)
            by2 = lerp(dy2 + 0.55, y_exit, tp)
            p2.draw_arrow(end_d, (x_exit, y_exit), color=(250, 204, 21), dashed=True)

        opp_ang2 = math.degrees(math.atan2(att_m[1] - opp_m[1], att_m[0] - opp_m[0]))
        att_ang2 = math.degrees(math.atan2(dy2 - att_m[1], dx2 - att_m[0]))

        p2.draw_robot(7.0, 0.5, 90, "GK", C_GK)
        p2.draw_robot(opp_m[0], opp_m[1], opp_ang2, "OPP", C_OPP)
        p2.draw_robot(att_m[0], att_m[1], att_ang2, "ATT", C_ATT)
        p2.draw_robot(dx2, dy2, ang2, "DEF", C_DEF, highlight=True)
        p2.draw_ball(bx2, by2)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "defender_has_ball.gif")

def make_defender_anchor():
    frames = []
    for i in range(N_FRAMES):
        t = i / (N_FRAMES - 1)
        im = Image.new("RGB", (W * SCALE, H * SCALE), (15, 23, 42))
        draw = ImageDraw.Draw(im)

        osc = 0.5 - 0.5 * math.cos(2 * math.pi * t)

        st1 = "Teammate attacking: Anchors 1 m outside penalty box at (7.0, 3.25)"
        sc1 = (99, 102, 241)
        p1 = PitchPanel(draw, (0, 0, W//2, H), y_range=(-0.8, 16.5),
                        title="3-Robot Squad: Central Box Anchor", status_text=st1, status_color=sc1)

        bx1 = lerp(3.5, 10.5, osc)
        by1 = 13.5
        def_pos = (7.0, 3.25)
        ang1 = math.degrees(math.atan2(by1 - def_pos[1], bx1 - def_pos[0]))

        p1.draw_dashed_line(def_pos, (bx1, by1), color=(148, 163, 184), width=1.5)
        p1.draw_dashed_line((3.25, 3.25), (10.75, 3.25), color=C_DEF, width=1.6)

        p1.draw_robot(7.0, 0.4, 90, "GK", C_GK)
        p1.draw_robot(bx1, by1, 90, "ATT", C_ATT)
        p1.draw_robot(lerp(8.5, 4.5, osc), 11.5, 90, "AST", C_AST)
        p1.draw_robot(def_pos[0], def_pos[1], ang1, "DEF", C_DEF, highlight=True)
        p1.draw_ball(bx1, by1 + 0.55)

        st2 = "Dual defenders offset laterally to split penalty arc coverage"
        sc2 = (16, 185, 129)
        p2 = PitchPanel(draw, (W//2, 0, W, H), y_range=(-0.8, 16.5),
                        title="4-Robot Squad: Shared Arc Coverage", status_text=st2, status_color=sc2)

        def1_p = (5.2, 3.25)
        def2_p = (8.8, 3.25)
        d1_ang = math.degrees(math.atan2(by1 - def1_p[1], bx1 - def1_p[0]))
        d2_ang = math.degrees(math.atan2(by1 - def2_p[1], bx1 - def2_p[0]))

        p2.draw_dashed_line(def1_p, (bx1, by1), color=(148, 163, 184), width=1.4)
        p2.draw_dashed_line(def2_p, (bx1, by1), color=(148, 163, 184), width=1.4)
        p2.draw_dashed_line((3.25, 3.25), (10.75, 3.25), color=C_DEF, width=1.6)

        p2.draw_robot(7.0, 0.4, 90, "GK", C_GK)
        p2.draw_robot(bx1, by1, 90, "ATT", C_ATT)
        p2.draw_robot(lerp(8.5, 4.5, osc), 11.5, 90, "AST", C_AST)
        p2.draw_robot(def1_p[0], def1_p[1], d1_ang, "DEF1", C_DEF, highlight=True)
        p2.draw_robot(def2_p[0], def2_p[1], d2_ang, "DEF2", C_DEF, highlight=True)
        p2.draw_ball(bx1, by1 + 0.55)

        draw.line([(W//2 * SCALE, 0), (W//2 * SCALE, H * SCALE)], fill=(15, 23, 42), width=2*SCALE)
        frames.append(im.resize((W, H), Image.Resampling.LANCZOS))
    save_gif(frames, "defender_anchor.gif")

if __name__ == "__main__":
    make_defender_set_piece()
    make_defender_shot_blocking()
    make_defender_has_ball()
    make_defender_anchor()
