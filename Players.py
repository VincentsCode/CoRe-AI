from Game import CoReInstance as Game

class Player1:
    def __init__(self, symbol):
        self.symbol = symbol

    def turn(self, board):
        for x in range(8):
            for y in range(8):
                if board[x][y] == "#":
                    return x, y
    
class Player2:
    def __init__(self, symbol):
        self.symbol = symbol

    def turn(self, board):
        for x in range(8):
            for y in range(8):
                if board[x][y] == "#":
                    return x, y


VISUALS_ON = True
if VISUALS_ON:
    import pygame
    pygame.init()

    size = width, height = 800, 800
    screen = pygame.display.set_mode(size)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    clock = pygame.time.Clock()

    screen.blit(background, (0, 0))

if __name__ == '__main__':
    g = Game()

    p1 = Player1("X")
    p2 = Player2("O")

    current_player = 1

    while True:
        t = p1.turn(g.board)

        if g.valid(t):
            g.turn(t)
            if g.won_check():
                print(g.board)
                exit()
        else:
            exit("Invalid turn of p1")

        t = p2.turn(g.board)

        if g.valid(t):
            g.turn(t)
            if g.won_check():
                print(g.board)
                exit()
        else:
            exit("Invalid turn of p2")
    
        print(g.board)
        
        if VISUALS_ON:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
            for x in range(8):
                for y in range(8):
                    pygame.draw.rect(screen, (0, 0, 0), [x*100, y*100, 100, 100], 3)
                    if g.board[x][y] != "#":
                        pygame.draw.circle(screen, (200, 0, 0), [x*100+50, y*100+50], 30, 0)
            

            pygame.display.flip()
            clock.tick(1)