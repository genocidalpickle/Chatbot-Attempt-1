import json
import random
import os

MEMORY_FILE = "data_set.json"
SYNONYMS_FILE = "synonyms.json"

# Load memory from file
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return {}

# Save memory to file
def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

# Load synonyms from file
def load_synonyms():
    if os.path.exists(SYNONYMS_FILE):
        with open(SYNONYMS_FILE, "r") as file:
            return json.load(file)
    return {}

# Save synonyms to file
def save_synonyms(synonyms):
    with open(SYNONYMS_FILE, "w") as file:
        json.dump(synonyms, file, indent=4)

# Initialize chatbot memory and synonyms
synonyms = load_synonyms()
memory = load_memory()

# Function to normalize user input and match key terms
def normalize_input(user_input):
    if not user_input:  # Check if None or empty
        return set()
    return set(user_input.lower().split())

# Function to find the main word in a synonym group
def find_main_word(user_input):
    user_input = normalize_input(user_input)  # Normalize user input to handle synonyms
    for key, values in synonyms.items():
        if any(word in values for word in user_input):
            return key
    return None

# Function to get the best response based on key words
def get_best_response(user_input):
    if not user_input:  # Ensure user_input is not None or empty
        return None  

    user_input = find_main_word(user_input)  # Find main word (may return None)
    
    if not user_input:  # If no synonym found, fallback to original input
        user_input = normalize_input(user_input)  # Convert to token set
    
    if not user_input:  # Ensure it's not empty after normalization
        return None

    for key, responses in memory.items():
        if any(word in key for word in user_input):
            sorted_responses = sorted(responses, key=lambda x: x.get("weight", 0), reverse=True)
            if sorted_responses:
                return random.choice(sorted_responses)["response"]
            else:
                print(f"Debug: No valid response found for {user_input}")
    return None



# Function to update responses based on feedback
def update_memory(user_input, response, feedback=None):
    user_input = find_main_word(user_input)  # Normalize user input to handle synonyms
    
    if user_input is None:
        user_input = " ".join(normalize_input(user_input))  # Fallback if no synonym found
    
    # Ensure memory structure is correct for new responses
    if user_input not in memory:
        memory[user_input] = [{"response": response, "weight": 5}]
    else:
        existing_responses = {r["response"]: r for r in memory[user_input]}
        
        if response in existing_responses:
            if feedback == "good":
                existing_responses[response]["weight"] += 1
            elif feedback == "bad":
                existing_responses[response]["weight"] -= 1
                
                # Remove response if weight drops to 0 or below
                if existing_responses[response]["weight"] <= 0:
                    memory[user_input].remove(existing_responses[response])
                    
                    # If no responses left for this input, forget it entirely
                    if not memory[user_input]:
                        del memory[user_input]
        else:
            # If the response doesn't exist, add it
            memory[user_input].append({"response": response, "weight": 1})

    save_memory(memory)

# Function to add a synonym
def add_synonym(main_word, synonym):
    if main_word in synonyms:
        if synonym not in synonyms[main_word]:
            synonyms[main_word].append(synonym)
    else:
        synonyms[main_word] = [synonym]
    
    save_synonyms(synonyms)

# Main chatbot loop
print("Chatbot is ready! Type 'exit' to stop.")

while True:
    user_input = input("You: ").strip().lower()
    if user_input == "exit":
        print("Goodbye!")
        break
        
    response = get_best_response(user_input)

    if response:
        print("Bot:", response)

        # Ask for feedback only if the bot gave a response
        feedback = input("Was this response good? (yes/no): ").strip().lower()
        if feedback == "yes":
            update_memory(user_input, response, "good")
        elif feedback == "no":
            print("Bot: Sorry")
            update_memory(user_input, response, "bad")  # Decrease weight
    else:
        # Only ask for a new response or synonym when the bot doesn't know how to respond
        print("Bot: I don't know how to respond. Would you like to add a synonym, or a new response? (n for new response/s for new synonym):")
        add_option = input().strip().lower()

        if add_option == "s":
            main_word = input("Enter the main word for the synonym (e.g., 'hello'): ").strip().lower()
            synonym = input(f"Enter a synonym for '{main_word}': ").strip().lower()
            add_synonym(main_word, synonym)
        elif add_option == "n":
            new_response = input("What should I say instead? ").strip()
            update_memory(user_input, new_response)
        else:
            print("Skipping. No action taken.")
