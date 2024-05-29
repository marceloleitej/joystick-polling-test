import time
import pygame
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt, QThread, Signal

# Inicialize o Pygame
pygame.init()
pygame.joystick.init()

class PollingRateWorker(QThread):
    pollingRateMeasured = Signal(int, float)

    def __init__(self, index):
        super().__init__()
        self.index = index
        self.running = True

    def run(self):
        joystick = pygame.joystick.Joystick(self.index)
        joystick.init()

        while self.running:
            start_time = time.time()
            poll_count = 0

            while time.time() - start_time < 1:
                for event in pygame.event.get():
                    if event.type == pygame.JOYAXISMOTION:
                        poll_count += 1

            end_time = time.time()
            total_time = end_time - start_time
            polling_rate = poll_count / total_time
            self.pollingRateMeasured.emit(self.index, polling_rate)

    def stop(self):
        self.running = False

class PollingRateApp(QWidget):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.joystick = pygame.joystick.Joystick(index)
        self.joystick_name = self.joystick.get_name()

        self.setWindowTitle(f"Joystick {self.joystick_name} Polling Rate Monitor")

        self.label = QLabel(f"{self.joystick_name}\nPolling Rate: -- Hz\nDelay: -- s\nDelay: -- ms", self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")

        info_text = (
            "1 - Jogos Competitivos e de Ação:\n"
            "500 Hz a 1000 Hz: Para jogos que requerem uma resposta rápida e precisa, como jogos de tiro em primeira pessoa (FPS) ou de ação rápida, uma taxa de polling alta (500 Hz ou superior) é ideal. Isso resulta em um delay muito baixo, proporcionando uma experiência de jogo mais responsiva.\n\n"
            "2 - Jogos Casuais e de Simulação:\n"
            "250 Hz a 500 Hz: Para jogos que não exigem uma resposta extremamente rápida, como jogos de simulação ou de estratégia, uma taxa de polling entre 250 Hz e 500 Hz é geralmente suficiente.\n\n"
            "3 - Uso Geral:\n"
            "125 Hz a 250 Hz: Para uso geral, como navegação em menus ou aplicações que não são sensíveis ao tempo, uma taxa de polling entre 125 Hz e 250 Hz é aceitável."
        )

        self.info_label = QTextEdit(self)
        self.info_label.setReadOnly(True)
        self.info_label.setPlainText(info_text)
        self.info_label.setStyleSheet("font-size: 14px; color: #ffffff; background-color: #333333; border: none;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

        self.setStyleSheet("background-color: #2c2c2c; padding: 10px;")

        self.polling_rate_worker = PollingRateWorker(index)
        self.polling_rate_worker.pollingRateMeasured.connect(self.update_polling_rate)
        self.polling_rate_worker.start()

    def update_polling_rate(self, index, rate):
        if index == self.index:
            delay_s = 1 / rate if rate > 0 else float('inf')
            delay_ms = delay_s * 1000  # Converte o delay para milissegundos
            self.label.setText(f"{self.joystick_name}\nPolling Rate: {rate:.2f} Hz\nDelay: {delay_s:.4f} s\nDelay: {delay_ms:.2f} ms")

    def closeEvent(self, event):
        self.polling_rate_worker.stop()
        self.polling_rate_worker.wait()

def main():
    # Verifique se há joysticks conectados
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("Nenhum joystick conectado.")
        return

    app = QApplication([])

    # Crie uma aplicação PollingRateApp para cada joystick
    windows = []
    for i in range(joystick_count):
        window = PollingRateApp(i)
        windows.append(window)
        window.show()

    app.exec()

if __name__ == "__main__":
    main()
