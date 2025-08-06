# Test file for unmatched parenthesis error
define m = Character("Matt", color="#0000FF")

label start:
    m "Hola, ¿cómo estás?"
    
    # Error específico: unmatched ')'
    m "({i}I wasn't struggling financially, but I wanted to have something to do besides having my face in a book when the school year started back up.{/i})"'
    
    m "Esto es una prueba"
    
    # Otros errores comunes
    m "Esta línea tiene una comilla sin cerrar"
    
    m "Esta línea tiene paréntesis sin balancear ("
    
    show 
    
    with
    
    jump
    
    menu:
    
    return 