import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import hashlib
import hmac
import re
import secrets
import time
import os
import sys
import threading
import pyperclip

class FizkSeedGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("FiZk Seed Generator")
        self.root.geometry("1280x720")  # Slightly larger window
        self.root.resizable(True, True)
        self.root.configure(bg="#1a1a2e")  # Darker, richer background
        
        try:
          self.root.iconbitmap("d:/Atharva/Projects/fizk/frontend/src/app/favicon.ico")
        except:
            pass

        # Set font configuration for better rendering
        self.default_font = ("Segoe UI", 11)  # Sharper font with increased size
        self.monospace_font = ("Consolas", 12)  # Sharper monospace font
        self.heading_font = ("Segoe UI", 20, "bold")
        self.subheading_font = ("Segoe UI", 12, "bold")
        
        # For detailed output
        self.details_window = None
        
        self.setup_styles()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_styles(self):
        # Configure the style for the application
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors - more vibrant and modern palette
        bg_color = "#1a1a2e"  # Dark blue background
        fg_color = "#e6e6e6"  # Slightly off-white text
        accent_color = "#4361ee"  # Vibrant blue
        accent_hover = "#3a56e8"  # Slightly darker when hovered
        secondary_color = "#3f37c9"  # Secondary accent
        
        # Configure styles
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=self.default_font)
        style.configure("TButton", 
                        background=accent_color, 
                        foreground="white", 
                        borderwidth=0,
                        font=self.default_font,
                        padding=[15, 8])  # More padding for buttons
                        
        style.map("TButton",
                 background=[("active", accent_hover), ("disabled", "#45456a")],
                 foreground=[("disabled", "#cccccc")])
        
        style.configure("Accent.TButton", 
                        background=secondary_color,
                        foreground="white", 
                        borderwidth=0,
                        font=(self.default_font[0], self.default_font[1], "bold"),
                        padding=[15, 10])
        
        style.map("Accent.TButton",
                 background=[("active", "#322da8"), ("disabled", "#45456a")],
                 foreground=[("disabled", "#cccccc")])
        
        style.configure("TRadiobutton", 
                        background=bg_color, 
                        foreground=fg_color, 
                        font=self.default_font)
        
        style.configure("TCheckbutton", 
                        background=bg_color, 
                        foreground=fg_color,
                        font=self.default_font)
        
        style.configure("TNotebook", 
                        background=bg_color,
                        borderwidth=0)
        
        style.configure("TNotebook.Tab", 
                        background="#252547", 
                        foreground=fg_color, 
                        padding=[15, 8],
                        font=self.default_font)
        
        style.map("TNotebook.Tab", 
                 background=[("selected", accent_color)],
                 foreground=[("selected", "#ffffff")])
        
        # Remove the focus dotted line
        style.configure(".", focuscolor=accent_color)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and description with improved styling
        title_label = ttk.Label(main_frame, text="FiZk Seed Generator", font=self.heading_font)
        title_label.pack(pady=(0, 12))
        
        # Add a subtle divider line
        divider = ttk.Separator(main_frame, orient="horizontal")
        divider.pack(fill=tk.X, pady=5)
        
        desc_label = ttk.Label(main_frame, 
                           text="Generate a secure 64-character hex seed for your FiZk account", 
                           font=self.default_font)
        desc_label.pack(pady=(5, 25))
        
        # Create notebook (tabbed interface) with improved styling
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Method tabs
        self.tab1 = ttk.Frame(notebook, padding=20)
        self.tab2 = ttk.Frame(notebook, padding=20)
        self.tab3 = ttk.Frame(notebook, padding=20)
        
        notebook.add(self.tab1, text="Entropy Mixing")
        notebook.add(self.tab2, text="Personal Mixer")
        notebook.add(self.tab3, text="Word Pattern")
        
        # Configure each tab
        self.setup_entropy_mixing_tab(self.tab1)
        self.setup_personal_mixer_tab(self.tab2)
        self.setup_word_pattern_tab(self.tab3)
        
        # Output frame with improved styling
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        output_label = ttk.Label(output_frame, text="Generated Seed:", font=self.subheading_font)
        output_label.pack(anchor="w", pady=(0, 8))
        
        # Seed output with improved styling
        self.output_seed = tk.Text(output_frame, 
                               height=3, 
                               font=self.monospace_font, 
                               bg="#0d0d1a", 
                               fg="#00ff7f", 
                               wrap=tk.WORD,
                               bd=2, 
                               relief=tk.RIDGE,
                               padx=10,
                               pady=10)
        self.output_seed.pack(fill=tk.X, expand=True)
        self.output_seed.config(state=tk.DISABLED)
        
        # Buttons frame with improved styling
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 5))
        
        self.copy_button = ttk.Button(buttons_frame, 
                                 text="Copy Result", # Changed from "Copy to Clipboard" to "Copy Result"
                                 command=self.copy_to_clipboard,
                                 style="Accent.TButton")
        self.copy_button.pack(side=tk.RIGHT, padx=5)
        self.copy_button.state(['disabled'])
        
        # Status bar with improved styling
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, 
                          textvariable=self.status_var, 
                          relief=tk.SUNKEN, 
                          anchor=tk.W,
                          padding=[10, 5],
                          background="#252547",
                          foreground="#a0a0d0")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))
        
    def setup_entropy_mixing_tab(self, tab):
        # Words input with improved styling
        words_frame = ttk.Frame(tab)
        words_frame.pack(fill=tk.X, pady=(0, 15))
        
        words_label = ttk.Label(words_frame, text="Enter your words or phrase:", font=self.subheading_font)
        words_label.pack(anchor="w", pady=(0, 8))
        
        self.words_input1 = scrolledtext.ScrolledText(words_frame, 
                                                 height=4, 
                                                 font=self.default_font,
                                                 wrap=tk.WORD, 
                                                 bd=0, 
                                                 relief=tk.FLAT,
                                                 padx=10,
                                                 pady=10,
                                                 background="#252547",
                                                 foreground="white")
        self.words_input1.pack(fill=tk.X)
        
        # Salt input with improved styling
        salt_frame = ttk.Frame(tab)
        salt_frame.pack(fill=tk.X, pady=15)
        
        salt_label = ttk.Label(salt_frame, text="Optional Salt (adds extra security):", font=self.default_font)
        salt_label.pack(anchor="w", pady=(0, 8))
        
        self.salt_input = ttk.Entry(salt_frame, 
                               font=self.default_font,
                               style="TEntry")
        self.salt_input.pack(fill=tk.X, ipady=5)  # More vertical padding
        
        # Random words option with improved styling
        random_frame = ttk.Frame(tab)
        random_frame.pack(fill=tk.X, pady=15)
        
        random_label = ttk.Label(random_frame, text="Or generate random words:", font=self.default_font)
        random_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.random_count1 = ttk.Spinbox(random_frame, from_=5, to=30, width=5, font=self.default_font)
        self.random_count1.set(15)
        self.random_count1.pack(side=tk.LEFT, padx=(0, 10))
        
        random_button = ttk.Button(random_frame, 
                               text="Generate Random Words", 
                               command=lambda: self.generate_random_words(self.words_input1, self.random_count1))
        random_button.pack(side=tk.LEFT)
        
        # Generate button with improved styling
        generate_frame = ttk.Frame(tab)
        generate_frame.pack(fill=tk.X, pady=(25, 10))
        
        self.detail_check1 = tk.BooleanVar()
        detail_checkbox = ttk.Checkbutton(generate_frame, 
                                     text="Show detailed processing info",
                                     variable=self.detail_check1,
                                     style="TCheckbutton")
        detail_checkbox.pack(side=tk.LEFT)
        
        generate_button = ttk.Button(generate_frame, 
                                 text="Generate Seed", 
                                 style="Accent.TButton",
                                 command=lambda: self.generate_seed(1))
        generate_button.pack(side=tk.RIGHT, padx=5)

    def setup_personal_mixer_tab(self, tab):
        # Words input with improved styling
        words_frame = ttk.Frame(tab)
        words_frame.pack(fill=tk.X, pady=(0, 15))
        
        words_label = ttk.Label(words_frame, text="Enter your words or phrase:", font=self.subheading_font)
        words_label.pack(anchor="w", pady=(0, 8))
        
        self.words_input2 = scrolledtext.ScrolledText(words_frame, 
                                                 height=4, 
                                                 font=self.default_font,
                                                 wrap=tk.WORD, 
                                                 bd=0, 
                                                 relief=tk.FLAT,
                                                 padx=10,
                                                 pady=10,
                                                 background="#252547",
                                                 foreground="white")
        self.words_input2.pack(fill=tk.X)
        
        # Personal info input with improved styling
        personal_frame = ttk.Frame(tab)
        personal_frame.pack(fill=tk.X, pady=15)
        
        personal_label = ttk.Label(personal_frame, text="Personal Information (e.g., name:John,year:1990):", 
                               font=self.default_font)
        personal_label.pack(anchor="w", pady=(0, 8))
        
        self.personal_input = ttk.Entry(personal_frame, font=self.default_font)
        self.personal_input.pack(fill=tk.X, ipady=5)  # More vertical padding
        
        # Personal info hint with improved styling
        hint_label = ttk.Label(personal_frame, 
                          text="Use information that only you would know and can remember",
                          font=(self.default_font[0], self.default_font[1] - 1),
                          foreground="#a0a0d0")
        hint_label.pack(anchor="w", pady=(8, 0))
        
        # Random words option with improved styling
        random_frame = ttk.Frame(tab)
        random_frame.pack(fill=tk.X, pady=15)
        
        random_label = ttk.Label(random_frame, text="Or generate random words:", font=self.default_font)
        random_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.random_count2 = ttk.Spinbox(random_frame, from_=5, to=30, width=5, font=self.default_font)
        self.random_count2.set(15)
        self.random_count2.pack(side=tk.LEFT, padx=(0, 10))
        
        random_button = ttk.Button(random_frame, 
                               text="Generate Random Words", 
                               command=lambda: self.generate_random_words(self.words_input2, self.random_count2))
        random_button.pack(side=tk.LEFT)
        
        # Generate button with improved styling
        generate_frame = ttk.Frame(tab)
        generate_frame.pack(fill=tk.X, pady=(25, 10))
        
        self.detail_check2 = tk.BooleanVar()
        detail_checkbox = ttk.Checkbutton(generate_frame, 
                                     text="Show detailed processing info",
                                     variable=self.detail_check2,
                                     style="TCheckbutton")
        detail_checkbox.pack(side=tk.LEFT)
        
        generate_button = ttk.Button(generate_frame, 
                                 text="Generate Seed", 
                                 style="Accent.TButton",
                                 command=lambda: self.generate_seed(2))
        generate_button.pack(side=tk.RIGHT, padx=5)

    def setup_word_pattern_tab(self, tab):
        # Words input with improved styling
        words_frame = ttk.Frame(tab)
        words_frame.pack(fill=tk.X, pady=(0, 15))
        
        words_label = ttk.Label(words_frame, text="Enter your words or phrase:", font=self.subheading_font)
        words_label.pack(anchor="w", pady=(0, 8))
        
        self.words_input3 = scrolledtext.ScrolledText(words_frame, 
                                                 height=4, 
                                                 font=self.default_font,
                                                 wrap=tk.WORD, 
                                                 bd=0, 
                                                 relief=tk.FLAT,
                                                 padx=10,
                                                 pady=10,
                                                 background="#252547",
                                                 foreground="white")
        self.words_input3.pack(fill=tk.X)
        
        # Pattern hint with improved styling
        hint_frame = ttk.Frame(tab)
        hint_frame.pack(fill=tk.X, pady=10)
        
        hint_label = ttk.Label(hint_frame, 
                          text="Best with 3+ distinctive words. Each word affects the entire seed pattern.",
                          font=(self.default_font[0], self.default_font[1] - 1),
                          foreground="#a0a0d0")
        hint_label.pack(anchor="w")
        
        # Random words option with improved styling
        random_frame = ttk.Frame(tab)
        random_frame.pack(fill=tk.X, pady=15)
        
        random_label = ttk.Label(random_frame, text="Or generate random words:", font=self.default_font)
        random_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.random_count3 = ttk.Spinbox(random_frame, from_=5, to=30, width=5, font=self.default_font)
        self.random_count3.set(15)
        self.random_count3.pack(side=tk.LEFT, padx=(0, 10))
        
        random_button = ttk.Button(random_frame, 
                               text="Generate Random Words", 
                               command=lambda: self.generate_random_words(self.words_input3, self.random_count3))
        random_button.pack(side=tk.LEFT)
        
        # Generate button with improved styling
        generate_frame = ttk.Frame(tab)
        generate_frame.pack(fill=tk.X, pady=(25, 10))
        
        self.detail_check3 = tk.BooleanVar()
        detail_checkbox = ttk.Checkbutton(generate_frame, 
                                     text="Show detailed processing info",
                                     variable=self.detail_check3,
                                     style="TCheckbutton")
        detail_checkbox.pack(side=tk.LEFT)
        
        generate_button = ttk.Button(generate_frame, 
                                 text="Generate Seed", 
                                 style="Accent.TButton",
                                 command=lambda: self.generate_seed(3))
        generate_button.pack(side=tk.RIGHT, padx=5)

    def setup_bindings(self):
        # Add key bindings
        self.root.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.root.bind("<Escape>", lambda e: self.close_details_window())

    def generate_random_words(self, text_widget, count_widget):
        count = int(count_widget.get())
        if count < 5 or count > 30:
            messagebox.showwarning("Invalid Count", "Please enter a number between 5 and 30")
            return
            
        # Expanded word list for better randomness
        simple_words = [
            "apple", "banana", "orange", "grape", "kiwi", "melon", "peach", "plum", "cherry", "lemon",
            "dog", "cat", "bird", "fish", "lion", "tiger", "bear", "wolf", "fox", "deer", "horse", "elephant",
            "red", "blue", "green", "yellow", "black", "white", "purple", "orange", "pink", "brown", "gray",
            "big", "small", "fast", "slow", "hot", "cold", "old", "new", "good", "bad", "tall", "short",
            "happy", "sad", "angry", "calm", "loud", "quiet", "rich", "poor", "brave", "afraid", "clever",
            "sun", "moon", "star", "cloud", "rain", "snow", "wind", "storm", "river", "mountain", "ocean",
            "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "hundred",
            "book", "chair", "table", "house", "door", "window", "phone", "computer", "pencil", "paper",
            "water", "fire", "earth", "air", "time", "space", "light", "dark", "north", "south", "east", "west"
        ]
        
        # Select random words
        result = []
        for _ in range(count):
            word_index = secrets.randbelow(len(simple_words))
            word = simple_words[word_index]
            result.append(word)
        
        random_words = " ".join(result)
        
        # Insert into text widget
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", random_words)
        
        self.status_var.set(f"Generated {count} random words")

    def generate_seed(self, method):
        # Get the appropriate inputs based on the method
        if method == 1:
            words = self.words_input1.get("1.0", tk.END).strip()
            salt = self.salt_input.get().strip()
            detail = self.detail_check1.get()
            personal_info = ""
        elif method == 2:
            words = self.words_input2.get("1.0", tk.END).strip()
            personal_info = self.personal_input.get().strip()
            detail = self.detail_check2.get()
            salt = ""
        elif method == 3:
            words = self.words_input3.get("1.0", tk.END).strip()
            detail = self.detail_check3.get()
            salt = ""
            personal_info = ""
        
        # Validate input
        if not words:
            messagebox.showwarning("Input Required", "Please enter some words or generate random words")
            return
            
        # Start generation in a separate thread
        self.status_var.set(f"Generating seed with Method {method}...")
        self.copy_button.state(['disabled'])
        self.output_seed.config(state=tk.NORMAL)
        self.output_seed.delete("1.0", tk.END)
        self.output_seed.insert("1.0", "Generating...\n(This may take a few seconds)")
        self.output_seed.config(state=tk.DISABLED)
        
        threading.Thread(target=self._run_generation, 
                        args=(method, words, salt, personal_info, detail)).start()

    def _run_generation(self, method, words, salt, personal_info, detail):
        try:
            # Generate the seed with detailed steps if requested
            seed, detailed_info = self.generate_seed_from_words_with_details(words, method, salt, personal_info, detail)
            
            # Update the UI with the result
            self.root.after(0, lambda: self._update_output(seed, detailed_info if detail else None))
        except Exception as e:
            # Store the error message before passing to lambda to avoid scope issues
            error_msg = str(e)
            self.root.after(0, lambda: self._show_error(error_msg))

    def _update_output(self, seed, detailed_info=None):
        self.output_seed.config(state=tk.NORMAL)
        self.output_seed.delete("1.0", tk.END)
        self.output_seed.insert("1.0", seed)
        self.output_seed.config(state=tk.DISABLED)
        
        self.status_var.set("Seed generated successfully!")
        self.copy_button.state(['!disabled'])
        
        # Show detailed information if available
        if detailed_info:
            self.show_details_window(detailed_info)

    def show_details_window(self, details):
        # Close any existing details window
        self.close_details_window()
        
        # Create a new window for details
        self.details_window = tk.Toplevel(self.root)
        self.details_window.title("Generation Details")
        self.details_window.geometry("700x500")
        self.details_window.configure(bg="#1a1a2e")
        
        # Make the window modal
        self.details_window.transient(self.root)
        self.details_window.grab_set()
        
        # Add a title
        title_frame = ttk.Frame(self.details_window, padding=15)
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, 
                           text="Seed Generation Details", 
                           font=self.subheading_font)
        title_label.pack(anchor=tk.W)
        
        # Add a scrolled text area for details
        details_text = scrolledtext.ScrolledText(self.details_window, 
                                           height=20, 
                                           width=80,
                                           font=("Consolas", 11),
                                           wrap=tk.WORD,
                                           padx=15,
                                           pady=15,
                                           background="#252547",
                                           foreground="#00ff7f")
        details_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Insert the details
        details_text.insert(tk.END, details)
        details_text.config(state=tk.DISABLED)
        
        # Add a close button
        button_frame = ttk.Frame(self.details_window, padding=15)
        button_frame.pack(fill=tk.X)
        
        close_button = ttk.Button(button_frame, 
                             text="Close", 
                             command=self.close_details_window)
        close_button.pack(side=tk.RIGHT)
        
        # Position the window relative to the main window
        self.details_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50))

    def close_details_window(self):
        if self.details_window and self.details_window.winfo_exists():
            self.details_window.destroy()
            self.details_window = None

    def _show_error(self, error_msg):
        self.output_seed.config(state=tk.NORMAL)
        self.output_seed.delete("1.0", tk.END)
        self.output_seed.config(state=tk.DISABLED)
        
        self.status_var.set(f"Error: {error_msg}")
        messagebox.showerror("Error", f"An error occurred: {error_msg}")

    def copy_to_clipboard(self):
        seed = self.output_seed.get("1.0", tk.END).strip()
        if seed and seed != "Generating...\n(This may take a few seconds)":
            pyperclip.copy(seed)
            self.status_var.set("Seed copied to clipboard!")
            
            # Store original text and change button text
            original_text = self.copy_button["text"]
            self.copy_button.config(text="Copied!")
            
            # Schedule changing back to original text after 2 seconds
            # Cancel any existing scheduled callback to avoid multiple callbacks
            if hasattr(self, '_copy_timer') and self._copy_timer is not None:
                self.root.after_cancel(self._copy_timer)
                
            self._copy_timer = self.root.after(2000, lambda: self.copy_button.config(text=original_text))

    # Seed Generation Methods with detailed output
    def clean_input(self, text):
        """Clean user input by normalizing whitespace"""
        return re.sub(r'\s+', ' ', text).strip()

    def method_1_entropy_mixing(self, words, salt="", detail=False):
        """
        Method 1: Entropy Mixing
        Mixes the entropy from all input words with custom salt using
        multiple hash functions and iterations.
        """
        details = []
        start_time = time.time()
        
        if detail:
            details.append("=" * 50)
            details.append("METHOD 1: ENTROPY MIXING")
            details.append("=" * 50)
            details.append("\nALGORITHM DESCRIPTION:")
            details.append("This method provides maximum security by combining multiple")
            details.append("cryptographic hash functions in sequence (SHA-512, SHA3-512, and BLAKE2b).")
            details.append("It performs 1000 rounds of hashing, with each round using a different")
            details.append("algorithm in rotation. This approach ensures thorough mixing of")
            details.append("input entropy and resistance against various cryptographic attacks.")
            details.append("\n" + "-" * 50)
            details.append("\nINPUT PARAMETERS:")
            details.append(f"• Words: \"{words}\"")
            details.append(f"• Salt: \"{salt or 'None'}\"")
            details.append(f"• Input length: {len(words)} characters")
        
        # Start with the basic input
        result = words.encode('utf-8')
        input_bytes = len(result)
        
        # Add salt if provided
        if salt:
            result = result + salt.encode('utf-8')
            if detail:
                details.append(f"• Combined input length: {len(result)} bytes")
                details.append(f"• Input+Salt (hex): {result.hex()[:32]}..." if len(result) > 16 else f"• Input+Salt (hex): {result.hex()}")
        elif detail:
            details.append(f"• Input bytes (hex): {result.hex()[:32]}..." if len(result) > 16 else f"• Input bytes (hex): {result.hex()}")
        
        if detail:
            details.append("\n" + "-" * 50)
            details.append("\nHASHING PROCESS (1000 iterations):")
            details.append(f"Initial data: {len(result)} bytes")
        
        # Perform multiple rounds of hashing with different algorithms
        for i in range(1000):
            algo_used = ""
            pre_hash = result[:16].hex() if len(result) > 16 else result.hex()
            
            if i % 3 == 0:
                result = hashlib.sha512(result).digest()
                algo_used = "SHA-512"
            elif i % 3 == 1:
                result = hashlib.sha3_512(result).digest()
                algo_used = "SHA3-512"
            else:
                result = hashlib.blake2b(result, digest_size=64).digest()
                algo_used = "BLAKE2b"
                
            # Add some iteration-specific data to prevent cycles
            result += str(i).encode('utf-8')
            
            # Only show certain iterations in detail to avoid overwhelming output
            if detail and (i < 3 or i == 9 or i == 99 or i == 499 or i == 999 or (i > 0 and i % 250 == 0)):
                details.append(f"Round {i+1:4d}: {algo_used:<8} → {pre_hash[:16]}... → {result[:10].hex()}...")
        
        # Final hash to get our 64-character output
        if detail:
            details.append(f"\nFinal data after 1000 rounds: {result[:20].hex()}...")
            details.append("\n" + "-" * 50)
            details.append("\nFINAL PROCESSING:")
        
        final_hash = hashlib.sha512(result).hexdigest()[:64]
        
        if detail:
            details.append(f"• SHA-512 of final data: {hashlib.sha512(result).hexdigest()[:20]}...")
            details.append(f"• Truncated to 64 chars: {final_hash}")
            details.append(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")
            details.append("\n" + "=" * 50)
            details.append("\nFINAL SEED (ready to use):")
            details.append(f"{final_hash}")
        
        return final_hash, "\n".join(details) if detail else ""

    def method_2_personal_mixer(self, words, personal_info="", detail=False):
        """
        Method 2: Personal Mixer
        Uses personal information mixed with words to create a seed that
        combines multiple personal factors with the input.
        """
        details = []
        start_time = time.time()
        
        if detail:
            details.append("=" * 50)
            details.append("METHOD 2: PERSONAL MIXER")
            details.append("=" * 50)
            details.append("\nALGORITHM DESCRIPTION:")
            details.append("This method uses HMAC (Hash-based Message Authentication Code) with")
            details.append("SHA3-512 to create a seed derived from your words and personal info.")
            details.append("It's designed to produce memorable yet secure seeds by mixing your")
            details.append("personal information with your base phrase. The algorithm uses a key")
            details.append("derived from your inputs and iteratively applies HMAC 2048 times,")
            details.append("evolving the key slightly on each iteration for added security.")
            details.append("\n" + "-" * 50)
            details.append("\nINPUT PARAMETERS:")
            details.append(f"• Base phrase: \"{words}\"")
            details.append(f"• Personal info: \"{personal_info or 'None'}\"")
        
        # Normalize inputs
        normalized_words = words.lower()
        
        if detail and normalized_words != words:
            details.append(f"• Normalized base phrase: \"{normalized_words}\"")
        
        # Create a base from words
        base = normalized_words.encode('utf-8')
        base_hex = base.hex()
        
        # Add personal info if provided
        if personal_info:
            personal_bytes = personal_info.encode('utf-8')
            personal_hex = personal_bytes.hex()
            base += personal_bytes
            if detail:
                details.append(f"• Personal info (hex): {personal_hex[:20]}..." if len(personal_hex) > 20 else f"• Personal info (hex): {personal_hex}")
                details.append(f"• Combined base (hex): {base.hex()[:20]}...")
        else:
            # Add some system-specific data for additional entropy
            pid = os.getpid()
            timestamp = time.time_ns()
            system_entropy = f"{pid}-{timestamp}"
            system_bytes = system_entropy.encode('utf-8')
            base += system_bytes
            if detail:
                details.append(f"• No personal info provided, using system entropy:")
                details.append(f"  - Process ID: {pid}")
                details.append(f"  - Timestamp: {timestamp}")
                details.append(f"• System entropy (hex): {system_bytes.hex()[:20]}...")
                details.append(f"• Combined base (hex): {base.hex()[:20]}...")
        
        # Create a unique key from the base data
        key = hashlib.sha3_256(base).digest()
        
        if detail:
            details.append("\n" + "-" * 50)
            details.append("\nHMAC PROCESS (2048 iterations):")
            details.append(f"• Initial key (SHA3-256): {key.hex()[:24]}...")
        
        # Use HMAC with multiple iterations
        result = base
        for i in range(2048):
            pre_result_hex = result[:12].hex()
            pre_key_hex = key[:12].hex()
            
            result = hmac.new(key, result, hashlib.sha3_512).digest()
            
            # Modify the key slightly each time
            key = hashlib.sha3_256(key + bytes([i & 0xFF])).digest()
            
            # Only show certain iterations in detail to avoid overwhelming output
            if detail and (i < 3 or i == 9 or i == 99 or i == 499 or i == 999 or i == 2047 or (i > 0 and i % 500 == 0)):
                details.append(f"Round {i+1:4d}: Key {pre_key_hex}... + Data {pre_result_hex}... → {result[:12].hex()}...")
        
        # Get final 64-character hex
        final_hash = result.hex()[:64]
        
        if detail:
            details.append("\n" + "-" * 50)
            details.append("\nFINAL PROCESSING:")
            details.append(f"• Final HMAC output: {result.hex()[:24]}...")
            details.append(f"• Truncated to 64 chars: {final_hash}")
            details.append(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")
            details.append("\n" + "=" * 50)
            details.append("\nFINAL SEED (ready to use):")
            details.append(f"{final_hash}")
        
        return final_hash, "\n".join(details) if detail else ""

    def method_3_diceware_style(self, words, detail=False):
        """
        Method 3: Word Pattern Mixing
        Treats each word as an element and mixes them in a
        deterministic but highly complex pattern.
        """
        details = []
        start_time = time.time()
        
        if detail:
            details.append("=" * 50)
            details.append("METHOD 3: WORD PATTERN MIXING")
            details.append("=" * 50)
            details.append("\nALGORITHM DESCRIPTION:")
            details.append("This method creates a unique pattern based on each word's")
            details.append("contribution. Unlike standard hashing that treats all input as")
            details.append("a single string, this algorithm hashes each word individually")
            details.append("with SHA-256 and then mixes these hashes byte-by-byte using")
            details.append("a position-dependent algorithm. This ensures that each word")
            details.append("distinctly influences the pattern of the final seed in a")
            details.append("deterministic way. The resulting byte array is then finalized")
            details.append("with SHA3-512 for the output seed.")
            details.append("\n" + "-" * 50)
            details.append("\nINPUT ANALYSIS:")
            details.append(f"• Original input: \"{words}\"")
        
        # Split words and ensure we have enough data
        word_list = self.clean_input(words).split()
        original_word_count = len(word_list)
        
        if detail:
            details.append(f"• Word count: {original_word_count}")
            if original_word_count > 0:
                details.append(f"• Words identified: {', '.join(word_list)}")
        
        if len(word_list) < 3:
            # Pad with repeated words if needed
            padding_needed = 3 - len(word_list)
            for i in range(padding_needed):
                padding_word = word_list[0] if word_list else "entropy"
                word_list.append(padding_word)
            
            if detail:
                details.append(f"• Padding added: {padding_needed} word(s) to reach minimum requirement of 3 words")
                details.append(f"• Final word list: {', '.join(word_list)}")
        
        if detail:
            details.append("\n" + "-" * 50)
            details.append("\nINDIVIDUAL WORD PROCESSING:")
        
        # Create initial bytes from words
        word_bytes = []
        for i, word in enumerate(word_list):
            # Get consistent bytes for each word
            word_hash = hashlib.sha256(word.encode('utf-8')).digest()
            word_bytes.append(word_hash)
            
            if detail:
                details.append(f"• Word {i+1:2d}: \"{word}\"")
                details.append(f"  - SHA-256: {word_hash.hex()[:32]}...")
        
        if detail:
            details.append("\n" + "-" * 50)
            details.append("\nPATTERN MIXING PROCESS:")
            details.append("Each byte position (0-63) of the output is determined by mixing")
            details.append("corresponding bytes from each word hash using XOR and rotation.")
        
        # Mix the bytes in a complex pattern
        mixed = bytearray(64)
        
        # Fill the mixed array using a pattern based on the words
        for i in range(64):
            byte_value = i
            for j, word_hash in enumerate(word_bytes):
                # Use different portions of each word hash based on position
                index = (i + j) % len(word_hash)
                # XOR the bytes in a rotating pattern
                byte_value ^= word_hash[index]
                # Add some position-dependent mixing
                byte_value = (byte_value + word_hash[(index * 3 + j) % len(word_hash)]) % 256
            
            mixed[i] = byte_value
            
            # Show only specific positions for clarity
            if detail and (i == 0 or i == 1 or i == 16 or i == 32 or i == 63):
                position_details = []
                for j, word_hash in enumerate(word_bytes):
                    idx1 = (i + j) % len(word_hash)
                    idx2 = (i * 2 + j) % len(word_hash)
                    position_details.append(f"Word {j+1}: {word_hash[idx1]:02x},{word_hash[idx2]:02x}")
                
                details.append(f"• Position {i:2d}: {','.join(position_details)} → {byte_value:02x}")
        
        if detail:
            details.append(f"\n• Mixed byte array: {mixed.hex()[:32]}...")
            details.append("\n" + "-" * 50)
            details.append("\nFINAL PROCESSING:")
        
        # Final processing with SHA3
        sha3_hash = hashlib.sha3_512(mixed).digest()
        result = sha3_hash.hex()[:64]
        
        if detail:
            details.append(f"• SHA3-512 of mixed array: {sha3_hash.hex()[:32]}...")
            details.append(f"• Truncated to 64 chars: {result}")
            details.append(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")
            details.append("\n" + "=" * 50)
            details.append("\nFINAL SEED (ready to use):")
            details.append(f"{result}")
        
        return result, "\n".join(details) if detail else ""

    def generate_seed_from_words_with_details(self, words, method=1, salt="", personal_info="", detail=False):
        """Generate a 64-character hex seed from words using the specified method"""
        
        words = self.clean_input(words)
        
        if method == 1:
            return self.method_1_entropy_mixing(words, salt, detail)
        elif method == 2:
            return self.method_2_personal_mixer(words, personal_info, detail)
        elif method == 3:
            return self.method_3_diceware_style(words, detail)
        else:
            raise ValueError(f"Invalid method: {method}. Choose 1, 2, or 3.")

    def generate_seed_from_words(self, words, method=1, salt="", personal_info="", detail=False):
        """Backwards compatibility wrapper that returns just the seed"""
        seed, _ = self.generate_seed_from_words_with_details(words, method, salt, personal_info, detail)
        return seed

if __name__ == "__main__":
    root = tk.Tk()
    app = FizkSeedGenerator(root)
    root.mainloop()