# -*- coding: utf-8 -*-
# game_manager.py - Quản lý trạng thái game và menu
import pygame
from Ui.menu import MainMenu
from Ui.spaceship_selector import SpaceshipSelector

class GameState:
    MENU = 0
    SPACESHIP_SELECT = 1
    GAME = 2

class GameManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = GameState.MENU
        
        # Initialize menus
        self.main_menu = MainMenu(width, height)
        self.spaceship_selector = SpaceshipSelector(width, height)
        
        # Sound flag (để tránh spam âm thanh)
        self.last_sound_event = None
    
    def update(self):
        """Cập nhật trạng thái hiện tại"""
        if self.state == GameState.MENU:
            self.main_menu.update()
        elif self.state == GameState.SPACESHIP_SELECT:
            self.spaceship_selector.update()
    
    def handle_event(self, event):
        """Xử lý events theo trạng thái hiện tại"""
        if self.state == GameState.MENU:
            return self.handle_menu_event(event)
        elif self.state == GameState.SPACESHIP_SELECT:
            return self.handle_spaceship_event(event)
        elif self.state == GameState.GAME:
            # Game events sẽ được xử lý trong main loop
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
                return "BACK_TO_MENU"
        
        return None
    
    def handle_menu_event(self, event):
        """Xử lý events của main menu"""
        result = self.main_menu.handle_event(event)
        
        if result == "PLAY_GAME":
            self.state = GameState.GAME
            return "START_GAME"
        elif result == "SELECT_SPACESHIP":
            self.state = GameState.SPACESHIP_SELECT
            return "BUTTON_CLICK"
        elif result == "EXIT_GAME":
            return "EXIT_GAME"
        elif result == "BUTTON_HOVER":
            return "BUTTON_HOVER"
        
        return None
    
    def handle_spaceship_event(self, event):
        """Xử lý events của spaceship selector"""
        result = self.spaceship_selector.handle_event(event)
        
        if result == "BACK_TO_MENU":
            self.state = GameState.MENU
            return "BUTTON_CLICK"
        elif result == "SHIP_SELECTED":
            # Quay về menu sau khi chọn phi thuyền
            self.state = GameState.MENU
            return "SHIP_SELECTED"
        elif result == "SHIP_CHANGED":
            return "BUTTON_HOVER"
        
        return None
    
    def draw(self, screen):
        """Vẽ theo trạng thái hiện tại"""
        if self.state == GameState.MENU:
            self.main_menu.draw(screen)
        elif self.state == GameState.SPACESHIP_SELECT:
            self.spaceship_selector.draw(screen)
        # Game drawing sẽ được xử lý trong main loop
    
    def is_in_menu(self):
        """Check xem có đang ở menu chính không"""
        return self.state == GameState.MENU
    
    def is_in_spaceship_select(self):
        """Check xem có đang ở menu chọn phi thuyền không"""
        return self.state == GameState.SPACESHIP_SELECT
    
    def is_in_game(self):
        """Check xem có đang ở game không"""
        return self.state == GameState.GAME
    
    def get_current_state(self):
        """Lấy trạng thái hiện tại"""
        return self.state