
# -*- coding: utf-8 -*-
"""
지뢰찾기 (Minesweeper) - 단일 파일 버전
- 좌클릭: 열기
- 폭탄을 피해 모든 빈 칸을 열면 승리
- 외부 이미지/폰트/데이터 없음 → PyInstaller로 바로 EXE 제작 가능

빌드 예시(윈도우):
    pyinstaller --onefile --windowed minesweeper_exe_ready.py
"""
import sys
from math import floor
import pygame
from random import randint
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# ----- 보드 설정 -----
WIDTH  = 20   # 가로 칸 개수
HEIGHT = 15   # 세로 칸 개수
SIZE   = 50   # 한 칸의 픽셀 크기 (SIZE x SIZE)

# ----- 내부 상태값 -----
EMPTY       = 0
BOMB        = 1
OPENED      = 2
NUM_OF_BOMBS = 20

# 전역(게임 진행 중 카운트/체크)
OPEN_COUNT = 0
CHECKED = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def num_of_bomb(field, x_pos, y_pos):
    """주변 8칸에 폭탄이 몇 개인지 세서 반환."""
    count = 0
    for yoffset in range(-1, 2):
        for xoffset in range(-1, 2):
            xpos, ypos = (x_pos + xoffset, y_pos + yoffset)
            if 0 <= xpos < WIDTH and 0 <= ypos < HEIGHT and field[ypos][xpos] == BOMB:
                count += 1
    return count

def open_tile(field, x_pos, y_pos):
    """
    (x_pos, y_pos) 칸을 열고, 주변이 0이면 연쇄적으로 확장 오픈.
    x_pos, y_pos는 픽셀 좌표가 아닌 '칸 인덱스'임.
    """
    global OPEN_COUNT, CHECKED

    # 이미 확인한 칸이면 바로 종료(재귀 폭주 방지)
    if CHECKED[y_pos][x_pos]:
        return
    CHECKED[y_pos][x_pos] = True

    # 자기 자신 포함 3x3 범위 처리
    for yoffset in range(-1, 2):
        for xoffset in range(-1, 2):
            xpos, ypos = (x_pos + xoffset, y_pos + yoffset)
            if 0 <= xpos < WIDTH and 0 <= ypos < HEIGHT and field[ypos][xpos] == EMPTY:
                field[ypos][xpos] = OPENED
                OPEN_COUNT += 1

                count = num_of_bomb(field, xpos, ypos)
                # 0칸이면 주변으로 퍼뜨리되, 현재 기준칸(x_pos, y_pos) 재호출은 생략
                if count == 0 and not (xpos == x_pos and ypos == y_pos):
                    open_tile(field, xpos, ypos)

def main():
    global OPEN_COUNT, CHECKED

    pygame.init()
    pygame.display.set_caption("지뢰찾기 - 단일 파일")
    SURFACE = pygame.display.set_mode((WIDTH * SIZE, HEIGHT * SIZE))
    FPSCLOCK = pygame.time.Clock()

    smallfont = pygame.font.SysFont(None, 36)
    largefont = pygame.font.SysFont(None, 72)
    message_clear = largefont.render("CLEARED!!", True, (0, 255, 255))
    message_over  = largefont.render("Game Over!!", True, (0, 255, 255))

    # 메시지 위치
    message_rect = message_clear.get_rect()
    message_rect.center = (WIDTH * SIZE / 2, HEIGHT * SIZE / 2)

    # 필드/상태 초기화
    field = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
    OPEN_COUNT = 0
    CHECKED = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    game_over = False

    # 폭탄 설치
    count = 0
    while count < NUM_OF_BOMBS:
        xpos, ypos = randint(0, WIDTH - 1), randint(0, HEIGHT - 1)
        if field[ypos][xpos] == EMPTY:
            field[ypos][xpos] = BOMB
            count += 1

    # 메인 루프
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                grid_x = floor(event.pos[0] / SIZE)
                grid_y = floor(event.pos[1] / SIZE)
                if 0 <= grid_x < WIDTH and 0 <= grid_y < HEIGHT:
                    if field[grid_y][grid_x] == BOMB:
                        game_over = True
                    else:
                        open_tile(field, grid_x, grid_y)

        # 배경
        SURFACE.fill((20, 20, 24))

        # 타일 그리기
        for ypos in range(HEIGHT):
            for xpos in range(WIDTH):
                tile = field[ypos][xpos]
                rect = pygame.Rect(xpos * SIZE, ypos * SIZE, SIZE, SIZE)

                if tile == EMPTY or tile == BOMB:
                    # 덮인 칸
                    pygame.draw.rect(SURFACE, (192, 192, 192), rect)

                    # 게임 오버면 폭탄 표시
                    if game_over and tile == BOMB:
                        # 폭탄을 노란 타원으로
                        pygame.draw.ellipse(SURFACE, (225, 225, 0), rect.inflate(-10, -10))

                elif tile == OPENED:
                    # 열린 칸 바탕
                    pygame.draw.rect(SURFACE, (230, 230, 230), rect)
                    # 숫자 표시
                    around = num_of_bomb(field, xpos, ypos)
                    if around > 0:
                        num_img = smallfont.render(f"{around}", True, (40, 40, 40))
                        # 숫자 중앙 배치
                        num_rect = num_img.get_rect(center=rect.center)
                        SURFACE.blit(num_img, num_rect.topleft)

        # 격자선
        for i in range(0, WIDTH * SIZE, SIZE):
            pygame.draw.line(SURFACE, (96, 96, 96), (i, 0), (i, HEIGHT * SIZE))
        for j in range(0, HEIGHT * SIZE, SIZE):
            pygame.draw.line(SURFACE, (96, 96, 96), (0, j), (WIDTH * SIZE, j))

        # 메시지
        if OPEN_COUNT == WIDTH * HEIGHT - NUM_OF_BOMBS:
            SURFACE.blit(message_clear, message_rect.topleft)
        elif game_over:
            SURFACE.blit(message_over, message_rect.topleft)

        pygame.display.update()
        FPSCLOCK.tick(60)

if __name__ == "__main__":
    main()
