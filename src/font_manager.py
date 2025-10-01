# -*- coding: utf-8 -*-
"""Quản lý font tiếng Việt và các helper render text.

Đặt imports lên đầu file; giữ các xử lý render nâng cao ở đây.
"""
import math
import pygame
from pathlib import Path

_ASSET_DIR = Path(__file__).parent.parent / "assets" / "fonts"

# Mapping logical names -> preferred system font names
PREFERRED = {
    "vn": ["Segoe UI", "Tahoma", "Arial"],
    "mono": ["Consolas", "Courier New", "DejaVu Sans Mono"]
}

def _find_ttf(name_hint):
    """Try find a TTF in assets/fonts that matches hint, else None."""
    if not _ASSET_DIR.exists():
        return None
    for p in _ASSET_DIR.iterdir():
        if p.suffix.lower() in (".ttf", ".otf") and name_hint.lower() in p.stem.lower():
            return str(p)
    # fallback: any ttf
    for p in _ASSET_DIR.iterdir():
        if p.suffix.lower() in (".ttf", ".otf"):
            return str(p)
    return None

def get_font(kind="vn", size=18, bold=False):
    """
    Return a pygame.font.Font instance.
    kind: 'vn' (ui), 'mono' (monospace) or any custom.
    """
    pygame.font.init()
    # try bundled ttf first (matching kind)
    ttf = _find_ttf(kind)
    if ttf:
        try:
            f = pygame.font.Font(ttf, size)
            f.set_bold(bold)
            return f
        except Exception:
            pass
    # try preferred system fonts
    prefs = PREFERRED.get(kind, [])
    for name in prefs:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f: 
                return f
        except Exception:
            continue
    # final fallback to default
    return pygame.font.Font(None, size)

# Module-level commonly used fonts (adjust sizes to taste)
font_vn = get_font("vn", 22, bold=True)
font_mono = get_font("mono", 16, bold=False)
font_large = get_font("vn", 48, bold=True)
font_small = get_font("vn", 20, bold=False)

class FontManager:
    def __init__(self):
        """Khởi tạo FontManager với hỗ trợ tiếng Việt tối ưu"""
        # Danh sách font ưu tiên cho tiếng Việt
        self.vietnamese_fonts = [
            # Fonts có hỗ trợ Unicode tốt nhất
            "Segoe UI",           # Windows mặc định, hỗ trợ tiếng Việt rất tốt
            "Arial Unicode MS",   # Hỗ trợ Unicode đầy đủ
            "Times New Roman",    # Serif font với hỗ trợ tiếng Việt
            "Arial",              # Sans-serif font phổ biến
            "Tahoma",             # Font Windows cũ nhưng ổn định
            "Verdana",            # Rõ ràng, dễ đọc
            "Calibri",            # Font Microsoft hiện đại
            "Microsoft Sans Serif", # Font hệ thống Windows
            "Consolas",           # Monospace font
            "Courier New",        # Monospace truyền thống
            "Comic Sans MS"       # Font thân thiện (backup)
        ]
        
        # Cache fonts để tránh load lại nhiều lần
        self.font_cache = {}
        
        # Test và tìm font tốt nhất
        self.best_font = self._find_best_vietnamese_font()
        
    def _find_best_vietnamese_font(self):
        """Tìm font tốt nhất cho tiếng Việt"""
        test_text = "Chơi Ngay - Àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữự"
        
        for font_name in self.vietnamese_fonts:
            try:
                # Test với size 24
                font = pygame.font.SysFont(font_name, 24)
                if font:
                    # Test render text tiếng Việt
                    test_surface = font.render(test_text, True, (255, 255, 255))
                    if test_surface and test_surface.get_width() > 50:  # Đủ rộng = render ok
                        return font_name
            except:
                continue
        
        # Fallback về font mặc định
        return "Arial"
        
    def get_font(self, size, bold=False, italic=False):
        """Lấy font với size và style cụ thể"""
        # Tạo key cho cache
        cache_key = (self.best_font, size, bold, italic)
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            if bold or italic:
                # Sử dụng SysFont với bold/italic
                font = pygame.font.SysFont(self.best_font, size, bold=bold, italic=italic)
            else:
                font = pygame.font.SysFont(self.best_font, size)
                
            # Cache font
            self.font_cache[cache_key] = font
            return font
            
        except Exception as e:
            # Fallback font
            try:
                fallback_font = pygame.font.Font(None, size)
                self.font_cache[cache_key] = fallback_font
                return fallback_font
            except:
                return None
    
    def render_text(self, text, size, color=(255, 255, 255), bold=False, italic=False, antialias=True, shadow=False, glow=False, outline=False):
        """Render text với font tối ưu cho tiếng Việt và các hiệu ứng đẹp"""
        font = self.get_font(size, bold, italic)
        if not font:
            return None
            
        try:
            # Render text chính với anti-aliasing cao
            main_surface = font.render(text, True, color)
            
            # Nếu không có hiệu ứng, trả về ngay
            if not (shadow or glow or outline):
                return main_surface
            
            # Tạo surface lớn hơn để chứa hiệu ứng
            text_width, text_height = main_surface.get_size()
            effect_padding = 6 if glow else 3 if outline else 2
            total_width = text_width + effect_padding * 2
            total_height = text_height + effect_padding * 2
            
            # Tạo surface trong suốt
            final_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
            
            # Vẽ shadow (nếu có)
            if shadow:
                shadow_color = (0, 0, 0, 180) if len(color) < 4 else (0, 0, 0, color[3] // 2)
                shadow_surface = font.render(text, True, shadow_color[:3])
                # Vẽ shadow offset
                final_surface.blit(shadow_surface, (effect_padding + 2, effect_padding + 2))
            
            # Vẽ outline (nếu có)
            if outline:
                outline_color = (0, 0, 0, 200) if len(color) < 4 else (0, 0, 0, color[3])
                outline_surface = font.render(text, True, outline_color[:3])
                # Vẽ outline ở các hướng
                directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                for dx, dy in directions:
                    final_surface.blit(outline_surface, (effect_padding + dx, effect_padding + dy))
            
            # Vẽ glow effect (nếu có)
            if glow:
                glow_color = tuple(min(255, c + 50) for c in color[:3])
                glow_surface = font.render(text, True, glow_color)
                # Vẽ glow ở nhiều layer với alpha giảm dần
                for radius in range(3, 0, -1):
                    alpha = 60 // radius
                    glow_copy = glow_surface.copy()
                    glow_copy.set_alpha(alpha)
                    for angle in range(0, 360, 45):
                        dx = int(radius * math.cos(math.radians(angle)))
                        dy = int(radius * math.sin(math.radians(angle)))
                        final_surface.blit(glow_copy, (effect_padding + dx, effect_padding + dy))
            
            # Vẽ text chính lên trên
            final_surface.blit(main_surface, (effect_padding, effect_padding))
            
            return final_surface
            
        except Exception as e:
            # Fallback về render thông thường
            try:
                return font.render(text, antialias, color)
            except:
                # Tạo surface trống nếu thất bại hoàn toàn
                surface = pygame.Surface((len(text) * size // 2, size))
                surface.fill((50, 50, 50))
                return surface
    
    def render_text_multiline(self, text, size, color=(255, 255, 255), max_width=None, line_spacing=5):
        """Render text nhiều dòng"""
        lines = text.split('\n')
        rendered_lines = []
        
        for line in lines:
            if max_width and line:
                # Chia dòng nếu quá dài
                words = line.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    test_surface = self.render_text(test_line, size, color)
                    if test_surface and test_surface.get_width() > max_width:
                        if current_line:
                            rendered_lines.append(self.render_text(current_line, size, color))
                        current_line = word
                    else:
                        current_line = test_line
                if current_line:
                    rendered_lines.append(self.render_text(current_line, size, color))
            else:
                rendered_lines.append(self.render_text(line, size, color))
        
        return rendered_lines
    
    def get_text_size(self, text, size):
        """Lấy kích thước của text"""
        font = self.get_font(size)
        if font:
            return font.size(text)
        return (0, 0)
    
    def test_vietnamese_support(self):
        """Test hỗ trợ tiếng Việt của font hiện tại"""
        test_cases = [
            "Chơi Ngay",
            "Lựa Chọn Phi Thuyền",
            "Thoát",
            "Àáảãạ - Ăằắẳẵặ - Âầấẩẫậ",
            "Èéẻẽẹ - Êềếểễệ",
            "Ìíỉĩị",
            "Òóỏõọ - Ôồốổỗộ - Ơờớởỡợ",
            "Ùúủũụ - Ưừứửữự",
            "Ỳýỷỹỵ - Đ/đ"
        ]
        
        all_good = True
        for test_text in test_cases:
            surface = self.render_text(test_text, 20)
            if surface:
                width = surface.get_width()
                if width <= 20:
                    all_good = False
            else:
                all_good = False
    
        return all_good


# Global font manager instance
font_manager = None

def get_font_manager():
    """Lấy font manager global"""
    global font_manager
    if font_manager is None:
        font_manager = FontManager()
    return font_manager

def render_vietnamese_text(text, size, color=(255, 255, 255), bold=False, italic=False):
    """Hàm tiện lợi để render text tiếng Việt"""
    fm = get_font_manager()
    return fm.render_text(text, size, color, bold, italic)

def render_title_text(text, size, color=(255, 255, 255)):
    """Render text cho tiêu đề với hiệu ứng shadow và glow"""
    fm = get_font_manager()
    return fm.render_text(text, size, color, bold=True, shadow=True, glow=True)

def render_button_text(text, size, color=(255, 255, 255), hover=False):
    """Render text cho button với hiệu ứng outline"""
    fm = get_font_manager()
    if hover:
        return fm.render_text(text, size, color, bold=True, outline=True, glow=True)
    else:
        return fm.render_text(text, size, color, bold=True, shadow=True)

def render_info_text(text, size, color=(200, 200, 200)):
    """Render text cho thông tin với hiệu ứng nhẹ"""
    fm = get_font_manager()
    return fm.render_text(text, size, color, shadow=True)