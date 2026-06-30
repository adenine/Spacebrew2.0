import tkinter as tk
from tkinter import messagebox

from tray_config import load_config, save_config


def main():
    config = load_config()
    root = tk.Tk()
    root.title("Spacebrew 2.0 Settings")
    root.resizable(False, False)

    tk.Label(root, text="MQTT Broker Address").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
    broker_var = tk.StringVar(value=config["broker"])
    tk.Entry(root, textvariable=broker_var, width=30).grid(row=1, column=0, padx=10)

    tk.Label(root, text="MQTT Broker Port").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 2))
    broker_port_var = tk.StringVar(value=str(config["broker_port"]))
    tk.Entry(root, textvariable=broker_port_var, width=30).grid(row=3, column=0, padx=10)

    tk.Label(root, text="Web Admin Port").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 2))
    web_port_var = tk.StringVar(value=str(config["web_port"]))
    tk.Entry(root, textvariable=web_port_var, width=30).grid(row=5, column=0, padx=10)

    tk.Label(
        root,
        text="Restart the server from the tray menu for changes to take effect.",
        wraplength=280,
        fg="gray",
        justify="left",
    ).grid(row=6, column=0, padx=10, pady=(10, 0), sticky="w")

    def on_save():
        try:
            new_config = {
                "broker": broker_var.get().strip() or "localhost",
                "broker_port": int(broker_port_var.get()),
                "web_port": int(web_port_var.get()),
            }
        except ValueError:
            messagebox.showerror("Invalid input", "Broker port and web port must be numbers.")
            return
        save_config(new_config)
        root.destroy()

    button_frame = tk.Frame(root)
    button_frame.grid(row=7, column=0, pady=10)
    tk.Button(button_frame, text="Cancel", command=root.destroy).pack(side="left", padx=5)
    tk.Button(button_frame, text="Save", command=on_save).pack(side="left", padx=5)

    root.mainloop()


if __name__ == "__main__":
    main()
