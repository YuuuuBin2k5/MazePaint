# sound_manager.py
import pygame
import os
from config import *

class SoundManager:
    def __init__(self):
        """Khởi tạo hệ thống âm thanh"""
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        
        self.sounds = {}
        self.music_playing = False
        self.victory_music_playing = False
        self.sound_enabled = SOUND_ENABLED
        self.current_music_type = "background"  # "background", "victory", "none"
        
        # Tải tất cả âm thanh
        self.load_sounds()
        
    def load_sounds(self):
        """Tải tất cả file âm thanh"""
        sound_files = {
            'move': SOUND_MOVE,
            'win': SOUND_WIN,
            'button': SOUND_BUTTON,
            'algorithm_start': SOUND_ALGORITHM_START,
            'algorithm_step': SOUND_ALGORITHM_STEP,
            'victory_celebration': VICTORY_PHASE3_SOUND
        }
        
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(SFX_VOLUME * MASTER_VOLUME)
                    self.sounds[name] = sound
                else:
                    print(f"⚠️  Sound file not found: {path}")
                    # Tạo âm thanh rỗng để tránh lỗi
                    self.sounds[name] = None
            except Exception as e:
                print(f"❌ Error loading {name}: {e}")
                self.sounds[name] = None
    
    def play_sound(self, sound_name, volume_multiplier=1.0):
        """Phát âm thanh hiệu ứng"""
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                sound = self.sounds[sound_name]
                sound.set_volume(SFX_VOLUME * MASTER_VOLUME * volume_multiplier)
                sound.play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
    
    def play_victory_music(self, loop=-1):
        """Phát nhạc chiến thắng"""
        if not self.sound_enabled:
            return
            
        try:
            if os.path.exists(VICTORY_MUSIC):
                pygame.mixer.music.load(VICTORY_MUSIC)
                pygame.mixer.music.set_volume(MUSIC_VOLUME * MASTER_VOLUME)
                pygame.mixer.music.play(loop)
                self.victory_music_playing = True
                self.current_music_type = "victory"
            else:
                print(f"⚠️  Victory music file not found: {VICTORY_MUSIC}")
        except Exception as e:
            print(f"❌ Error playing victory music: {e}")
    
    def play_background_music(self, loop=-1):
        """Phát nhạc nền"""
        if not self.sound_enabled:
            return
            
        try:
            if os.path.exists(BACKGROUND_MUSIC):
                pygame.mixer.music.load(BACKGROUND_MUSIC)
                pygame.mixer.music.set_volume(MUSIC_VOLUME * MASTER_VOLUME)
                pygame.mixer.music.play(loop)
                self.music_playing = True
                self.current_music_type = "background"
            else:
                print(f"⚠️  Background music file not found: {BACKGROUND_MUSIC}")
        except Exception as e:
            print(f"❌ Error playing background music: {e}")

    def play_music(self, loop=-1):
        """Phát nhạc nền (wrapper cho tương thích ngược)"""
        self.play_background_music(loop)
    
    def stop_music(self):
        """Dừng nhạc nền"""
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.victory_music_playing = False
            self.current_music_type = "none"
        except Exception as e:
            print(f"Error stopping music: {e}")
    
    def pause_music(self):
        """Tạm dừng nhạc nền"""
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Error pausing music: {e}")
    
    def unpause_music(self):
        """Tiếp tục nhạc nền"""
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Error unpausing music: {e}")
    
    def set_sound_enabled(self, enabled):
        """Bật/tắt âm thanh"""
        self.sound_enabled = enabled
        if not enabled:
            self.stop_music()
    
    def set_master_volume(self, volume):
        """Điều chỉnh âm lượng chính (0.0 - 1.0)"""
        volume = max(0.0, min(1.0, volume))  # Đảm bảo trong khoảng 0-1
        
        # Cập nhật âm lượng cho tất cả sound effects
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(SFX_VOLUME * volume)
        
        # Cập nhật âm lượng nhạc nền
        pygame.mixer.music.set_volume(MUSIC_VOLUME * volume)
    
    def play_move_sound(self):
        """Âm thanh di chuyển"""
        self.play_sound('move', 0.7)
    
    def play_win_sound(self):
        """Âm thanh chiến thắng"""
        self.play_sound('win', 1.0)
    
    def play_button_sound(self):
        """Âm thanh nhấn nút"""
        self.play_sound('button', 0.8)
    
    def play_algorithm_start_sound(self):
        """Âm thanh bắt đầu thuật toán"""
        self.play_sound('algorithm_start', 0.9)
    
    def play_algorithm_step_sound(self):
        """Âm thanh từng bước thuật toán"""
        self.play_sound('algorithm_step', 0.4)
    
    def play_victory_celebration_sound(self):
        """Âm thanh đặc biệt cho phase 3 victory"""
        self.play_sound('victory_celebration', 1.0)
    
    def switch_to_background_music(self):
        """Chuyển về nhạc nền"""
        if self.current_music_type != "background":
            self.play_background_music()
    
    def switch_to_victory_music(self):
        """Chuyển sang nhạc chiến thắng"""
        if self.current_music_type != "victory":
            self.play_victory_music()

# Tạo instance global
sound_manager = SoundManager()