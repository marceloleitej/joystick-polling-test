import time
import threading
import pygame
import tkinter as tk
from tkinter import ttk
import queue

# Inicialize o Pygame
pygame.init()
pygame.joystick.init()

class PollingRateApp:
    def __init__(self, root, joystick, index, q):
        self.root = root
        self.joystick = joystick
        self.joystick_name = joystick.get_name()
        self.index = index
        self.q = q

        # Informações sobre as taxas de polling ideais
        info_text = (
            "1 - Jogos Competitivos e de Ação:\n"
            "500 Hz a 1000 Hz: Para jogos que requerem uma resposta rápida e precisa, como jogos de tiro em primeira pessoa (FPS) ou de ação rápida, uma taxa de polling alta (500 Hz ou superior) é ideal. Isso resulta em um delay muito baixo, proporcionando uma experiência de jogo mais responsiva.\n\n"
            "2 - Jogos Casuais e de Simulação:\n"
            "250 Hz a 500 Hz: Para jogos que não exigem uma resposta extremamente rápida, como jogos de simulação ou de estratégia, uma taxa de polling entre 250 Hz e 500 Hz é geralmente suficiente.\n\n"
            "3 - Uso Geral:\n"
            "125 Hz a 250 Hz: Para uso geral, como navegação em menus ou aplicações que não são sensíveis ao tempo, uma taxa de polling entre 125 Hz e 250 Hz é aceitável."
        )

        # Configuração da interface
        self.label = ttk.Label(root, text=f"{self.joystick_name}\nPolling Rate: -- Hz\nDelay: -- s\nDelay: -- ms", font=("Helvetica", 16))
        self.label.grid(row=index, column=0, padx=10, pady=10, sticky="W")

        self.info_label = ttk.Label(root, text=info_text, font=("Helvetica", 12), wraplength=400)
        self.info_label.grid(row=index + 1, column=0, padx=10, pady=10, sticky="W")

        self.polling_rate = 0
        self.running = True

        self.update_rate_thread = threading.Thread(target=self.measure_polling_rate)
        self.update_rate_thread.start()

        self.update_label()

    def measure_polling_rate(self):
        while self.running:
            start_time = time.time()
            poll_count = 0

            while time.time() - start_time < 1:
                pygame.event.pump()
                poll_count += 1
                time.sleep(0.001)  # 1ms sleep para reduzir a carga da CPU

            end_time = time.time()
            total_time = end_time - start_time
            self.polling_rate = poll_count / total_time

            # Coloca o resultado na fila
            self.q.put((self.index, self.polling_rate))

    def update_label(self):
        try:
            while True:
                index, rate = self.q.get_nowait()
                if index == self.index:
                    delay_s = 1 / rate if rate > 0 else float('inf')
                    delay_ms = delay_s * 1000  # Converte o delay para milissegundos
                    self.label.config(text=f"{self.joystick_name}\nPolling Rate: {rate:.2f} Hz\nDelay: {delay_s:.4f} s\nDelay: {delay_ms:.2f} ms")
        except queue.Empty:
            pass
        self.root.after(100, self.update_label)

    def on_closing(self):
        self.running = False
        self.update_rate_thread.join()

def main():
    # Verifique se há joysticks conectados
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("Nenhum joystick conectado.")
        return

    # Crie uma instância Tkinter
    root = tk.Tk()
    root.title("Joystick Polling Rate Monitor")

    # Fila para comunicação entre threads
    q = queue.Queue()

    # Crie uma aplicação PollingRateApp para cada joystick
    apps = []
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        app = PollingRateApp(root, joystick, i, q)
        apps.append(app)

    # Configurar o protocolo de fechamento da janela
    def on_closing():
        for app in apps:
            app.on_closing()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
