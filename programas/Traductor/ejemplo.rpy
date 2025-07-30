# Example Ren'Py script file for translation testing
# This file contains typical visual novel dialogue and structure

# Character definitions
define e = Character("Emma", color="#c8ffc8")
define m = Character("Mike", color="#c8c8ff")
define n = Character(None, kind=nvl)

# Game start
label start:
    scene bg room
    with fade
    
    "Welcome to our visual novel!"
    "This is a test file for the translator."
    
    e "Hello! My name is Emma."
    e "I'm excited to meet you today."
    
    m "Hi Emma! I'm Mike."
    m "It's nice to meet you too."
    
    e "How are you doing today?"
    m "I'm doing great, thanks for asking!"
    
    n "The story continues with more dialogue and character interactions."
    n "This is a longer text that should be translated properly."
    
    e "I love reading books and watching movies."
    e "What about you? What do you like to do?"
    
    m "I enjoy playing video games and listening to music."
    m "Sometimes I also like to cook new recipes."
    
    "The characters continue their conversation about their hobbies and interests."
    
    e "That sounds really interesting!"
    e "Maybe we could hang out together sometime?"
    
    m "That would be great! I'd love to spend more time with you."
    m "We could go to the park or visit a café."
    
    "The story progresses as the characters get to know each other better."
    
    n "This is a narrative text that provides context for the story."
    n "It helps set the mood and atmosphere for the scene."
    
    e "I'm really glad we met today."
    e "You're such a nice person to talk to."
    
    m "I feel the same way about you."
    m "I hope we can become good friends."
    
    "The scene ends with a warm feeling between the characters."
    
    return 