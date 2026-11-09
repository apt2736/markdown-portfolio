import math
from PIL import Image, ImageDraw, ImageFont

SCALE = 2  # 2x supersampling for crisp anti-aliasing
W, H = 720, 380
CAPTION_H = 46

def get_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size * SCALE)
        except Exception:
            pass
    return ImageFont.load_default()

def ease(t):
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)

def lerp(a, b, t):
    return a + (b - a) * t

class PitchPanel:
    """Tightly fitted MSL pitch panel with bottom-exclusive caption."""
    def __init__(self, draw, rect, y_range=(0.0, 22.0), title="", status_text="", status_color=(30, 64, 175)):
        self.draw = draw
        x0, y0, x1, y1 = [v * SCALE for v in rect]
        self.rect = (x0, y0, x1, y1)
        self.y_min, self.y_max = y_range
        self.x_min, self.x_max = -0.5, 14.5

        cap_h = CAPTION_H * SCALE
        self.pitch_rect = (x0, y0, x1, y1 - cap_h)
        self.caption_rect = (x0, y1 - cap_h, x1, y1)

        # Draw green turf filling the pitch area completely - zero border
        draw.rectangle(self.pitch_rect, fill=(29, 107, 58))

        # Pitch coordinate mapping
        avail_w = self.pitch_rect[2] - self.pitch_rect[0]
        avail_h = self.pitch_rect[3] - self.pitch_rect[1]
        world_w = self.x_max - self.x_min
        world_h = self.y_max - self.y_min
        self.ppm = min(avail_w / world_w, avail_h / world_h)

        used_w = world_w * self.ppm
        used_h = world_h * self.ppm
        self.ox = self.pitch_rect[0] + (avail_w - used_w) / 2.0
        self.oy = self.pitch_rect[1] + (avail_h - used_h) / 2.0

        self._draw_pitch()
        self._draw_bottom_caption(title, status_text, status_color)

    def to_px(self, x, y):
        px = self.ox + (x - self.x_min) * self.ppm
        py = self.oy + (self.y_max - y) * self.ppm
        return (px, py)

    def len_px(self, m):
        return m * self.ppm

    def _draw_pitch(self):
        d = self.draw

        # Alternating stripes
        for y_stripe in range(0, 24, 2):
            y_top = min(self.y_max, max(self.y_min, y_stripe + 2))
            y_bot = min(self.y_max, max(self.y_min, y_stripe))
            if y_top > y_bot:
                p1 = self.to_px(0, y_top)
                p2 = self.to_px(14, y_bot)
                color = (34, 120, 66) if (y_stripe // 2) % 2 == 0 else (29, 107, 58)
                d.rectangle([p1[0], p1[1], p2[0], p2[1]], fill=color)

        lw = max(2, int(1.8 * SCALE))
        line_col = (230, 240, 235)

        # Sidelines
        p_tl = self.to_px(0, min(22.0, self.y_max))
        p_br = self.to_px(14, max(0.0, self.y_min))
        d.line([(p_tl[0], p_tl[1]), (p_tl[0], p_br[1])], fill=line_col, width=lw)
        d.line([(p_br[0], p_tl[1]), (p_br[0], p_br[1])], fill=line_col, width=lw)

        # Home goal & line
        if self.y_min <= 0.0 <= self.y_max:
            d.line([self.to_px(0, 0), self.to_px(14, 0)], fill=line_col, width=lw)
            g1 = self.to_px(5.0, 0.0)
            g2 = self.to_px(9.0, -0.55)
            d.rectangle([g1[0], g1[1], g2[0], g2[1]], fill=(191, 219, 254), outline=(255, 255, 255), width=lw)

        # Away goal & line
        if self.y_min <= 22.0 <= self.y_max:
            d.line([self.to_px(0, 22), self.to_px(14, 22)], fill=line_col, width=lw)
            g1 = self.to_px(5.0, 22.55)
            g2 = self.to_px(9.0, 22.0)
            d.rectangle([g1[0], g1[1], g2[0], g2[1]], fill=(254, 202, 202), outline=(255, 255, 255), width=lw)

        # Home Penalty Box (y: 0 to 2.25, x: 3.25 to 10.75)
        if self.y_min < 2.25:
            y_b = max(0.0, self.y_min)
            p1 = self.to_px(3.25, min(2.25, self.y_max))
            p2 = self.to_px(10.75, y_b)
            d.rectangle([p1[0], p1[1], p2[0], p2[1]], outline=line_col, width=lw)
        if self.y_min < 0.75:
            y_b = max(0.0, self.y_min)
            p1 = self.to_px(4.75, min(0.75, self.y_max))
            p2 = self.to_px(9.25, y_b)
            d.rectangle([p1[0], p1[1], p2[0], p2[1]], outline=line_col, width=lw)

        # Away Penalty Box (y: 19.75 to 22)
        if self.y_max > 19.75:
            y_t = min(22.0, self.y_max)
            p1 = self.to_px(3.25, y_t)
            p2 = self.to_px(10.75, max(19.75, self.y_min))
            d.rectangle([p1[0], p1[1], p2[0], p2[1]], outline=line_col, width=lw)
        if self.y_max > 21.25:
            y_t = min(22.0, self.y_max)
            p1 = self.to_px(4.75, y_t)
            p2 = self.to_px(9.25, max(21.25, self.y_min))
            d.rectangle([p1[0], p1[1], p2[0], p2[1]], outline=line_col, width=lw)

        # Halfway line & center circle
        if self.y_min <= 11.0 <= self.y_max:
            d.line([self.to_px(0, 11), self.to_px(14, 11)], fill=line_col, width=lw)
        if self.y_min <= 13.0 and self.y_max >= 9.0:
            pts = []
            for deg in range(0, 365, 5):
                rad = math.radians(deg)
                cx_w = 7.0 + 2.0 * math.cos(rad)
                cy_w = 11.0 + 2.0 * math.sin(rad)
                if self.y_min <= cy_w <= min(22.0, self.y_max):
                    pts.append(self.to_px(cx_w, cy_w))
                else:
                    if len(pts) > 1:
                        d.line(pts, fill=line_col, width=lw)
                    pts = []
            if len(pts) > 1:
                d.line(pts, fill=line_col, width=lw)

    def _draw_bottom_caption(self, title, status_text, status_color):
        d = self.draw
        cx0, cy0, cx1, cy1 = self.caption_rect
        # Solid dark footer bar
        d.rectangle([cx0, cy0, cx1, cy1], fill=(15, 23, 42))
        # Top accent dividing line between pitch and caption
        d.line([(cx0, cy0), (cx1, cy0)], fill=(51, 65, 85), width=max(1, int(1.5 * SCALE)))

        # Status indicator dot
        dot_r = 4.5 * SCALE
        dot_cx = cx0 + 14 * SCALE
        dot_cy = cy0 + 13 * SCALE
        d.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=status_color)

        # Line 1: Scenario Title
        font_title = get_font(10.5, bold=True)
        d.text((cx0 + 26 * SCALE, cy0 + 6 * SCALE), title, fill=(255, 255, 255), font=font_title)

        # Line 2: Detailed Tactical Description / Action
        font_desc = get_font(9.0, bold=False)
        d.text((cx0 + 14 * SCALE, cy0 + 24 * SCALE), status_text, fill=(203, 213, 225), font=font_desc)

    def draw_badge(self, *args, **kwargs):
        # Exclusively display captions at the bottom; no-op for in-pitch badges
        pass

    def draw_line(self, p1_world, p2_world, color=(255, 255, 255), width=2):
        self.draw.line([self.to_px(*p1_world), self.to_px(*p2_world)], fill=color, width=int(width * SCALE))

    def draw_dashed_line(self, p1_world, p2_world, color=(255, 255, 255), width=2, dash_len=0.4, gap_len=0.25):
        x1, y1 = p1_world
        x2, y2 = p2_world
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist < 1e-4:
            return
        dx, dy = (x2 - x1) / dist, (y2 - y1) / dist
        s = 0.0
        while s < dist:
            e = min(dist, s + dash_len)
            sp = self.to_px(x1 + dx * s, y1 + dy * s)
            ep = self.to_px(x1 + dx * e, y1 + dy * e)
            self.draw.line([sp, ep], fill=color, width=int(width * SCALE))
            s += dash_len + gap_len

    def draw_arrow(self, p1_world, p2_world, color=(250, 204, 21), width=2.5, dashed=False, head_size=0.45):
        if dashed:
            self.draw_dashed_line(p1_world, p2_world, color=color, width=width)
        else:
            self.draw.line([self.to_px(*p1_world), self.to_px(*p2_world)], fill=color, width=int(width * SCALE))
        x1, y1 = p1_world
        x2, y2 = p2_world
        ang = math.atan2(y2 - y1, x2 - x1)
        p_tip = self.to_px(x2, y2)
        p_left = self.to_px(x2 - head_size * math.cos(ang - 0.45), y2 - head_size * math.sin(ang - 0.45))
        p_right = self.to_px(x2 - head_size * math.cos(ang + 0.45), y2 - head_size * math.sin(ang + 0.45))
        self.draw.polygon([p_tip, p_left, p_right], fill=color)

    def draw_dashed_circle(self, center_world, radius_m, color=(251, 191, 36), width=2, num_dashes=28):
        cx, cy = center_world
        for i in range(num_dashes):
            a1 = (2 * math.pi * i) / num_dashes
            a2 = (2 * math.pi * (i + 0.55)) / num_dashes
            pts = []
            for k in range(5):
                a = a1 + (a2 - a1) * (k / 4.0)
                pts.append(self.to_px(cx + radius_m * math.cos(a), cy + radius_m * math.sin(a)))
            self.draw.line(pts, fill=color, width=int(width * SCALE))

    def draw_arc_segment(self, center_world, radius_m, deg_start, deg_end, color=(56, 189, 248), width=2.5, dashed=True):
        cx, cy = center_world
        steps = 36
        pts = []
        for i in range(steps + 1):
            a = math.radians(deg_start + (deg_end - deg_start) * (i / steps))
            pts.append((cx + radius_m * math.cos(a), cy + radius_m * math.sin(a)))
        for i in range(len(pts) - 1):
            if not dashed or (i % 2 == 0):
                self.draw.line([self.to_px(*pts[i]), self.to_px(*pts[i+1])], fill=color, width=int(width * SCALE))

    def draw_cone(self, apex_world, target_world, half_angle_deg, length_m, outline_color=(252, 165, 165)):
        ax, ay = apex_world
        tx, ty = target_world
        base_ang = math.atan2(ty - ay, tx - ax)
        ha = math.radians(half_angle_deg)
        p_apex = self.to_px(ax, ay)
        pts = [p_apex]
        for i in range(15):
            a = base_ang - ha + (2 * ha * i) / 14.0
            pts.append(self.to_px(ax + length_m * math.cos(a), ay + length_m * math.sin(a)))
        self.draw.polygon(pts, outline=outline_color, width=int(1.6 * SCALE))
        for r_frac in [0.35, 0.65, 0.9]:
            arc_pts = []
            for i in range(11):
                a = base_ang - ha + (2 * ha * i) / 10.0
                arc_pts.append(self.to_px(ax + length_m * r_frac * math.cos(a), ay + length_m * r_frac * math.sin(a)))
            self.draw.line(arc_pts, fill=outline_color, width=int(1.2 * SCALE))

    def draw_robot(self, x, y, theta_deg, label="ATT", role_color=(14, 165, 233), highlight=False):
        px, py = self.to_px(x, y)
        r = max(11 * SCALE, self.len_px(0.58))
        if highlight:
            hr = r + 4 * SCALE
            self.draw.ellipse([px - hr, py - hr, px + hr, py + hr], outline=(250, 204, 21), width=int(2.2 * SCALE))
        self.draw.ellipse([px - r, py - r, px + r, py + r], fill=(15, 23, 42), outline=(255, 255, 255), width=int(1.8 * SCALE))
        ir = r * 0.72
        self.draw.ellipse([px - ir, py - ir, px + ir, py + ir], fill=role_color)
        rad = math.radians(theta_deg)
        nx = px + r * 0.95 * math.cos(rad)
        ny = py - r * 0.95 * math.sin(rad)
        lx = px + r * 0.45 * math.cos(rad + 0.55)
        ly = py - r * 0.45 * math.sin(rad + 0.55)
        rx = px + r * 0.45 * math.cos(rad - 0.55)
        ry = py - r * 0.45 * math.sin(rad - 0.55)
        self.draw.polygon([(nx, ny), (lx, ly), (rx, ry)], fill=(255, 255, 255))

        font = get_font(8, bold=True)
        bbox = self.draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if math.sin(rad) < -0.35:
            ly_off = py - r - th - 5 * SCALE
        else:
            ly_off = py + r + 3 * SCALE
        self.draw.rounded_rectangle(
            [px - tw/2 - 3*SCALE, ly_off - 1*SCALE, px + tw/2 + 3*SCALE, ly_off + th + 3*SCALE],
            radius=3*SCALE, fill=(15, 23, 42), outline=role_color, width=1*SCALE
        )
        self.draw.text((px - tw/2, ly_off), label, fill=(255, 255, 255), font=font)

    def draw_ball(self, x, y):
        px, py = self.to_px(x, y)
        r = max(5 * SCALE, self.len_px(0.24))
        self.draw.ellipse([px - r, py - r, px + r, py + r], fill=(250, 204, 21), outline=(15, 23, 42), width=int(1.8 * SCALE))
