import pygame
import numpy as np

def dist(a, b):
    """Вычисляет евклидово расстояние между двумя точками(a и b) - на паре делали"""
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def brush(pos):
    """Генерирует точки - на паре делали"""
    near_points = []
    for i in range(np.random.randint(1, 7)): # Создаем случайное количество точек от 1 до 7
        x = pos[0] + np.random.randint(-20, 20) # Смещаем по x в пределах [-20, 20]
        y = pos[1] + np.random.randint(-20, 20) # Смещаем по y в пределах [-20, 20]
        near_points.append((x, y))
    return near_points

def region_query(points, point, eps):
    """Нахождение соседей точки(points) в радиусу(eps) от точки(point)"""
    neighbors = []
    for idx, p in enumerate(points):
        # Проверяем каждую точку, находится ли она в пределах радиуса eps
        if dist(point, p) <= eps:
            neighbors.append(idx)
    return neighbors

def dbscan(points, eps, min_samples):
    """Реализация алгоритма DBSCAN"""
    labels = [-1] * len(points)  # Изначально все точки имеют метку = -1
    cluster_id = 0 # Идентификатор текущего кластера, начнем с нуля

    for i in range(len(points)):
        if labels[i] != -1:  # Если точка уже обработана(т.е. != -1), пропускаем
            continue

        neighbors = region_query(points, points[i], eps)  # Ищем соседей для текущей точки

        # Если недостаточно соседей, помечаем точку как шум, иначе создаем новый кластер и расширяем его
        if len(neighbors) < min_samples:
            labels[i] = 0
        else:
            cluster_id += 1
            grow_cluster(points, labels, i, neighbors, cluster_id, eps, min_samples)

    return labels

def grow_cluster(points, labels, point_idx, neighbors, cluster_id, eps, min_samples):
    """Расширение кластера"""
    labels[point_idx] = cluster_id # Назначаем точке текущий кластер

    i = 0
    # обрабатываем всех соседей с учетом расширения(neighbors тоже растет)
    while i < len(neighbors):
        neighbor_idx = neighbors[i]

        # Если точка была шумом
        if labels[neighbor_idx] == 0:
            labels[neighbor_idx] = cluster_id # Делаем её частью кластера

        # Если точка ещё не обработана
        elif labels[neighbor_idx] == -1:
            labels[neighbor_idx] = cluster_id # Делаем её частью кластера
            new_neighbors = region_query(points, points[neighbor_idx], eps) # Находим соседей текущей точки
            if len(new_neighbors) >= min_samples:
                neighbors += new_neighbors # # Если достаточно соседей, добавляем новых соседей в общий список(neighbors)

        i += 1

def draw_points(screen, points, labels=None, cluster_colors=None):
    """Отображение точек на экране"""
    for idx, point in enumerate(points):
        color = "black" if labels is None else cluster_colors.get(labels[idx], "gray")
        pygame.draw.circle(screen, color, point, 5)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE) # Создаем окно
    screen.fill("white") # Заполняем белым фоном

    radius = 3 # Радиус точек
    points = []  # Список всех точек
    labels = None # Метки кластеров
    cluster_colors = {} # Словарь цветов кластеров
    is_pressed = False  # Флаг нажатия кнопки мыши

    running = True # Основной цикл программы
    while running:
        for event in pygame.event.get():
            # Обработка выхода из программы
            if event.type == pygame.QUIT:
                running = False

            # При изменении размера окна перерисовываем точки
            elif event.type == pygame.WINDOWRESIZED:
                screen.fill("white")
                draw_points(screen, points, labels, cluster_colors)

            # Нажали кнокпу мыши -> началось нажатие <=> is_pressed = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                is_pressed = True

            # Отжали кнокпу мыши -> закончилось нажатие <=> is_pressed = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                is_pressed = False

            # Прожали кнопку мыши и ведем по экрану
            elif event.type == pygame.MOUSEMOTION and is_pressed:
                pos = event.pos # Текущая позиция мыши
                if len(points) == 0 or dist(pos, points[-1]) > 20:
                    near_points = brush(pos)  # Генерируем рандомные точки кисти около точки
                    # Рисуем рандомные точки и добавляеи их в массив всех точек
                    for point in near_points:
                        pygame.draw.circle(screen, "black", point, radius)
                        points.append(point)
                    # Рисуем точку и добавляем ее в массив всех точек
                    pygame.draw.circle(screen, "black", pos, radius)
                    points.append(pos)

            # Нажали Enter => запускаем DBSCAN
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    eps = 50  # Радиус поиска соседей
                    min_samples = 3  # Минимальное количество соседей для кластера
                    labels = dbscan(points, eps, min_samples)  # Выполняем кластеризацию

                    # Генерация случайных цветов для кластеров
                    unique_labels = set(labels)
                    cluster_colors = {label: (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
                                      for label in unique_labels if label != 0}
                    cluster_colors[0] = "red"  # Шумовые точки помечены красным

        # Обновляем экран
        screen.fill("white")
        draw_points(screen, points, labels, cluster_colors) # Рисуем все точки
        pygame.display.flip()  # Обновляем дисплей

    pygame.quit()

if __name__ == "__main__":
    main()