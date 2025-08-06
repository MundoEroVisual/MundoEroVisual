# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.
define m = Character("[name]", color="#0000FF")
define slowdissolve = Dissolve(3.0)
define mg = Character("Sr. Galmeir", color="#ff8800")
define g = Character("Chica", color="#ea00ff")
define v = Character("Victoria", color="#ea00ff")

# El juego comienza aquí.
label splashscreen:
    scene splashscreen with slowdissolve
    show text "{color=#ffffff}ADVERTENCIA: El juego contiene contenido sexual. Todos los personajes son mayores de 18 años. Se recomienda discreción.{/color}" with slowdissolve
    pause 3.5
    hide text with slowdissolve
    scene blank_screen with slowdissolve
    
    image introvid = Movie(channel="xss", play="/images/introvid.webm", loop=False)
    show introvid with dissolve
    pause 4.0
    hide introvid with slowdissolve
    pause 1.0
    play music playdead fadein 5
    
    image introvid2 = Movie(channel="xrus", play="/images/introvid2.webm", loop=False)
    show introvid2 with dissolve
    pause 9.8
    hide introvid2 with slowdissolve
    pause 1.0
    return

label start:
    $ renpy.transition(slowdissolve)
    scene blank_screen with slowdissolve
    pause 1.0
    scene scene1 with slowdissolve
    pause 1.0
    show presentstitle1 at truecenter with dissolve
    pause 1.5
    scene scene1b with slowdissolve
    pause 1.0
    scene scene2 with slowdissolve
    pause 1.0
    show presentstitle2 at truecenter with dissolve
    pause 1.5
    scene scene2b with slowdissolve
    pause 1.0
    scene scene3 with slowdissolve
    pause 1.0
    show presentstitle3 at truecenter with dissolve
    pause 1.5
    scene scene3b with slowdissolve
    pause 1.0
    scene blank_screen with slowdissolve
    stop music fadeout 12
    
    python:
        name = renpy.input("¿Cómo te llamas? (Deja en blanco para 'Matt').", length=15)
        name = name.strip() or "Matt"
    
    scene scene4 with slowdissolve
    m "¿Hmm?"
    m "({i}*suspiro* Parece que se coló de nuevo.{/i})"
    m "({i}Este último mes ha sido una locura total.{/i})"
    m "({i}A veces me pregunto cómo habrían sido las cosas si todo hubiera salido diferente.{/i})"
    
    scene scene5 with dissolve
    m "({i}Es extraño cómo una pequeña decisión puede cambiarlo todo.{/i})"
    
    scene scene6 with dissolve
    m "({i}...una acción simple puede poner tu vida patas arriba.{/i})"
    
    scene scene7 with dissolve
    pause 0.5
    
    scene scene8 with Dissolve(2.0)
    m "({i}...y una simple mirada... puede cambiar el destino.{/i})"
    
    scene blank_screen with slowdissolve
    pause 0.5
    show gametitle at truecenter with slowdissolve
    pause 1.0
    scene blank_screen with slowdissolve
    pause 1.0
    play ambience quiet_office fadein 3
    scene scene9 with slowdissolve
    pause 0.5
    show onemonthago at truecenter with slowdissolve
    pause 1.0
    scene scene10 with slowdissolve
    pause 0.5
    scene scene11 with dissolve
    m "¿Entonces? ¿Qué opinas?"
    mg "¿Quieres la respuesta honesta?"
    
    scene scene12 with dissolve
    m "Eh... ¿sí? Por eso lo entregué."
    
    scene scene13 with dissolve
    mg "Sinceramente, creo que estás asumiendo demasiado."
    mg "Tu trabajo es definitivamente superior al promedio, pero con las clases por venir, no creo que puedas con toda la carga."
    
    scene scene14 with dissolve
    m "Con todo respeto, señor, creo que puedo manejar ambas cosas."
    
    scene scene15 with dissolve
    mg "'Puedes hacer dos cosas a la vez, pero no puedes concentrarte efectivamente en dos cosas a la vez.'"
    
    scene scene16 with dissolve
    m "...Gary Keller."
    
    scene scene17 with dissolve
    mg "¡Exactamente!"
    
    scene scene18 with dissolve
    mg "Eres un trabajador incansable, [name]. La mejor ética de trabajo que he visto en mucho tiempo."
    mg "Pero no quiero verte fracasar. Tendrás nuestras puertas abiertas cuando termine el semestre."
    
    scene scene19 with dissolve
    m "G-gracias, señor."
    
    play ambience outsiderain fadeout 3 fadein 3
    scene scene20 with slowdissolve
    m "({i}Y así... me quedé sin trabajo durante el último mes del verano.{/i})"
    m "({i}No estaba en apuros económicos, pero quería hacer algo más que meter la cara en los libros cuando comenzara el nuevo curso.{/i})"
    
    scene scene21 with dissolve
    m "({i}Mi padre y yo dejamos esta ciudad cuando estaba en primaria, cuando lo trasladaron por trabajo.{/i})"
    m "({i}Después de que tuvo que mudarse al extranjero por un ascenso, ya no tenía motivos para quedarme en nuestra nueva ciudad, así que decidí regresar a mi ciudad natal.{/i})"
    
    scene scene22 with dissolve
    m "({i}A pesar de haber crecido aquí, era bastante solitario, y no interactuaba con mucha gente de mi edad.{/i})"
    m "({i}Cuando me mudé, no había muchas personas que me diera pena dejar atrás, y nadie a quien tuviera ganas de volver a ver.{/i})"
    
    scene scene23 with dissolve
    m "({i}A pesar de que mi padre es muy rico, no soportaba la idea de vivir a costa de otros, y estaba decidido a generar mis propios ingresos.{/i})"
    m "({i}Eventualmente ahorré lo suficiente para tener mi propio lugar, pero me costaba encontrar algo con qué ocupar mi tiempo.{/i})"
    m "({i}No conocer a nadie en la ciudad no ayudaba mucho.{/i})"
    
    scene scene24 with dissolve
    m "({i}Pero una sola interacción aquel día lluvioso volviendo de la oficina...{/i})"
    
    scene scene25 with Dissolve(2.0)
    m "({i}...cambiaría por completo el último mes de mi verano.{/i})"
    
    scene scene26 with dissolve
    m "({i}Nunca fui bueno con las mujeres.{/i})"
    
    scene scene27 with dissolve
    m "({i}No era porque fuera feo ni nada, simplemente nunca sabía qué decir.{/i})"
    
    scene scene28 with dissolve
    m "({i}Siempre decía algo estúpido o estaba en el lugar equivocado en el momento equivocado.{/i})"
    
    scene scene29 with dissolve
    m "({i}Tampoco era alguien que creyera en el destino o el azar.{/i})"
    
    scene scene30 with dissolve
    m "({i}Así que, sea lo que sea que me hizo ser el héroe ese día...{/i})"
    
    scene scene31 with dissolve
    m "({i}Me metió en una situación más grande de lo que cualquier héroe podría manejar.{/i})"
    
    scene scene32 with slowdissolve
    m "({i}...mucho más grande.{/i})"
    
    scene blank_screen with slowdissolve
    pause 1.0
    show gametitle at truecenter with slowdissolve
    pause 1.0
    scene blank_screen with slowdissolve
    stop music fadeout 3
    pause 1.0
    show dayslater at truecenter with slowdissolve
    pause 1.0
    hide dayslater with slowdissolve
    play ambience cityblockday fadeout 3 fadein 3
    pause 0.5
    scene scene33 with slowdissolve
    m "S-sí señor. Entiendo."
    m "Gracias. Adiós."
    stop ambience fadeout 3
    
    scene scene34 with slowdissolve
    m "({i}Otra entrevista fallida.{/i})"
    
    scene scene35 with dissolve
    m "({i}Con las clases a solo unas semanas, no tenía idea de cómo iba a pasar el resto del verano.{/i})"
    
    scene scene36 with dissolve
    m "({i}Tal vez alguna solicitud de trabajo llegó por correo.{/i})"
    
    play ambience cityblockday fadein 3
    scene scene37 with slowdissolve
    pause 0.5
    scene scene38 with dissolve
    m "({i}...nope. Solo correo basura.{/i})"
    
    scene scene39 with dissolve
    m "({i}A este paso, solo estudiaré y dormiré todo el semestre.{/i})"
    
    scene scene40 with dissolve
    m "¿Hmm?"
    
    scene scene41 with dissolve
    m "..."
    
    scene scene42 with dissolve
    m "({i}Espera un segundo.{/i})"
    m "¿Hola?"
    
    scene scene43 with dissolve
    g "*jadeo*"
    m "¿Hay alguien ahí?"
    
    scene scene44 with dissolve
    pause 0.5
    scene scene45 with dissolve
    m "..."
    m "Eh, no voy a morder."
    
    scene scene46 with Dissolve(2.0)
    m "({i}Una chica...{/i})"
    m "Eh, ¿hay una razón por la que te escondes?"
    m "Si quieres hablar, no tienes que ser tímida."
    
    scene scene47 with dissolve
    g "..."
    
    scene scene48 with slowdissolve
    m "({i}¿Hmm?{/i})"
    m "({i}Espera... ¿es la chica del otro día?{/i})"
    
    scene scene49 with dissolve
    m "({i}Nunca supe su nombre.{/i})"
    m "({i}Después del incidente simplemente... se fue corriendo.{/i})"
    m "({i}Ahora que puedo verla bien... es bastante linda.{/i})"
    
    scene scene50 with dissolve
    m "Eh, hola. Me llamo [name]."
    m "Eres la chica del otro día, ¿cierto?"
    
    scene scene51 with dissolve
    v "Sí. Soy Victoria."
    
    scene scene52 with dissolve
    m "¿Victoria, eh? Es un bonito nombre."
    m "Nunca tuve la oportunidad de hablar contigo después de... ya sabes."
    m "¿Estás bien?"
    
    scene scene53 with dissolve
    v "..."
    m "({i}¿Hmm? ¿Es tímida?{/i})"
    m "¿Hola? ¿Victoria?"
    
    scene scene54 with dissolve
    v "Muchas gracias, y... estoy bien."
    
    scene scene55 with dissolve
    m "Me alegra escuchar eso. Me preocupé cuando saliste corriendo."
    m "Entonces, eh... ¿qué te trae por aquí?"
    m "({i}¿Cómo sabe dónde vivo?{/i})"
    
    scene scene56 with dissolve
    v "Solo quería... agradecerte como es debido."
    v "No tuve oportunidad de hacerlo el otro día."
    
    scene scene57 with dissolve
    m "Oh, no tienes que hacer eso."
    m "Solo hice lo que cualquiera haría."
    
    scene scene58 with dissolve
    v "No, lo digo en serio."
    v "Te debo la vida."
    
    scene scene59 with dissolve
    m "({i}Wow, se lo toma muy en serio.{/i})"
    m "Bueno, o sea... no hice mucho."
    m "Pero si realmente quieres, no me voy a oponer."
    
    scene scene60 with dissolve
    m "Entonces, ¿qué tenías en mente?"
    
    scene scene61 with dissolve
    v "Umm... cierra los ojos."
    
    scene scene62 with dissolve
    m "¿Q-qué? ¿Por qué debería-?"
    
    scene scene63 with dissolve
    v "Solo hazlo."
    
    scene scene64 with dissolve
    m "O-okey."
    
    scene blank_screen with dissolve
    m "({i}No sé por qué, pero sentí la necesidad de hacer lo que decía.{/i})"
    m "({i}¿Por qué me pediría que-?{/i})"
    
    scene scene65 with dissolve
    m "¡¡¡!!!"
    m "({i}¡¿Q-qué?!{/i})"
    
    scene scene66 with dissolve
    m "({i}¡¿Un beso?!{/i})"
    
    scene scene67 with dissolve
    m "({i}¡¿Y no un beso cualquiera, sino un beso francés?!{/i})"
    
    scene scene68 with Dissolve(2.0)
    m "({i}¡Jamás esperé que hiciera eso!{/i})"
    
    scene scene69 with dissolve
    v "Eres buen besador."
    
    scene scene70 with dissolve
    m "¿G-gracias?"
    m "({i}No sé cómo sentirme con esto.{/i})"
    m "({i}Digo, le salvé la vida, pero...{/i})"
    
    scene scene71 with dissolve
    m "({i}No esperaba que fuera tan... directa.{/i})"
    m "({i}Pero... no puedo decir que no me gustó.{/i})"
    m "({i}Será mejor que vuelva adentro antes de que esto se salga de control.{/i})"
    
    scene scene72 with dissolve
    m "Me... alegra haberte salvado, pero... de verdad tengo que irme ahora."
    v "..."
    
    scene blank_screen with slowdissolve
    pause 1.0
    show dayslater at truecenter with slowdissolve
    pause 1.0
    scene blank_screen with slowdissolve
    pause 1.0
    scene scene73 with slowdissolve
    m "({i}Pasaron unos días y no había señales de Victoria.{/i})"
    m "({i}Pero entonces, de la nada...{/i})"
    
    scene scene75 with dissolve
    pause 1.0
    scene scene76 with slowdissolve
    m "({i}...ella regresó.{/i})"
    
    scene scene77 with dissolve
    m "({i}Pensé que si la ignoraba se iría.{/i})"
    
    scene scene78 with Dissolve(2.0)
    m "({i}Pero día tras día...{/i})"
    
    scene scene79 with Dissolve(2.0)
    m "({i}...seguía volviendo.{/i})"
    
    play ambience outsiderain fadeout 3 fadein 3
    scene scene80 with slowdissolve
    pause 1.0
    scene scene81 with slowdissolve
    m "*suspiro*"
    m "({i}Esto se está volviendo ridículo.{/i})"
    
    scene scene82 with dissolve
    m "({i}¿De verdad está parada ahí bajo la lluvia?{/i})"
    m "({i}Si sigue así seguro se va a enfermar.{/i})"
    
    scene scene83 with dissolve
    m "({i}E-espera un segundo...{/i})"
    m "({i}¿No está usando sostén?{/i})"
    
    scene scene84 with dissolve
    m "..."
    m "({i}Maldita sea. Por supuesto que me ve mirando.{/i})"
    
    scene scene85 with dissolve
    v "Hola."
    
    scene scene86 with dissolve
    m 'Sí, no me vengas con un "Hola".'
    
    scene scene87 with dissolve
    m "¿Qué puede ser tan importante como para quedarte bajo la lluvia?"
    m "Te vas a enfermar si sigues ahí."
    
    scene scene88 with dissolve
    v "...¿bueno? ¿No me vas a invitar a pasar?"
    
    scene scene89 with dissolve
    m "({i}Esta chica es un problema.{/i})"
    
    scene scene90 with dissolve
    m "({i}Pero dadas las circunstancias...{/i})"
    
    scene scene91 with dissolve
    m "*suspiro* Está bien, pero solo hasta que pase la lluvia."
    v "Mhm."
    m "({i}Sí... definitivamente un problema.{/i})"
    
    stop ambience fadeout 3
    scene scene92 with slowdissolve
    pause 1.0
    scene scene93 with slowdissolve
    m "Bueno, dijeron que la lluvia debería parar en unas horas, así que-"
    
    scene scene94 with dissolve
    m "({i}...y me está ignorando.{/i})"
    
    scene scene95 with dissolve
    v "Bonito lugar."
    
    scene scene96 with dissolve
    m "*suspiro* Gracias, supongo."
    
    scene scene97 with dissolve
    v "Entonces... ¿y ahora qué?"
    
    scene scene98 with dissolve
    m "({i}Problemas.{/i})"
    m "B-bueno, iré a ver si tengo algo seco que puedas usar, para empezar."
    m "¿Podrías intentar no romper nada mientras tanto?"
    v "Mhm."
    m "*suspiro*"
    
    scene scene99 with slowdissolve
    show fewminlater at truecenter with slowdissolve
    pause 1.0
    hide fewminlater with slowdissolve
    m "Bien, ya estoy de vuelta."
    
    scene scene100 with dissolve
    m "Lo mejor que pude encontrar fue-"
    
    scene scene101 with dissolve
    m "..."
    m "({i}¿Se fue?{/i})"
    
    scene scene102 with dissolve
    m "({i}No tengo idea de qué pasa por la cabeza de esta chica.{/i})"
    m "({i}Definitivamente parecía-{/i})"
    
    scene scene103 with Dissolve(2.0)
    pause 0.5
    scene scene104 with Dissolve(2.0)
    pause 0.5
    scene scene105 with Dissolve(2.0)
    m "."
    m ".."
    m "..."
    m "({i}¡¿Qué demonios?!{/i})"
    
    scene scene106 with dissolve
    v "Oh, ya regresaste."
    
    scene scene107 with dissolve
    m "Sí, entonces... ¿me puedes decir por qué decidiste que mi cama era el mejor lugar para esperar?"
    
    scene scene108 with dissolve
    v "Bueno, porque es cómoda."
    
    scene scene109 with dissolve
    m "B-bueno, sí, pero-"
    "*aclara la garganta*"
    
    scene scene110 with dissolve
    m "De todas formas, no tengo ropa de mujer, pero encontré una camisa extragrande que podrías usar."
    m "Pondré tu ropa mojada en la secadora, pero puedes usar esto mientras termina."
    
    scene scene111 with dissolve
    v "¡Está bien!"
    m "¡W-woah!"
    
    scene scene112 with dissolve
    m "¿Qué estás haciendo?"
    
    scene scene113 with dissolve
    v "Umm... ¿quitándome la ropa? ¿Cómo más la vas a secar?"
    
    scene scene114 with dissolve
    m "({i}Eso... es un buen punto.{/i})"
    m "P-pero, ¿no puedes esperar a que salga de la habitación, al menos?"
    
    scene scene115 with dissolve
    v "Nah, eso parece mucho caminar de más."
    v "Puedes quitártela mientras estás aquí."
    
    scene scene116 with dissolve
    m "({i}¡Santo cielo!{/i})"
    m "({i}Está medio desnuda... en mi casa.{/i})"
    
    scene scene117 with dissolve
    m "({i}Aunque no puedo quejarme mucho. Esos pechos son simplemente...{/i})"
    
    scene scene118 with dissolve
    m "({i}E-espera, ¿qué está-{/i})"
    m "¡E-espera!"
    
    scene scene119 with dissolve
    v "Tranquilo. Tengo puesto pantis..."
    m "Eso... no es realmente el problema aquí."
    
    scene scene120 with dissolve
    m "({i}Mentiría si dijera que no es hermosa.{/i})"
    m "({i}¿Pero qué onda con ella? ¿Por qué parece tan cómoda con un extraño?{/i})"
    m "({i}Necesito saber por qué se está comportando así.{/i})"
    
    scene scene121 with dissolve
    m "Oye, ¿crees que podamos hablar un poco? Estoy confundido sobre algunas cosas."
    
    scene scene122 with dissolve
    v "¡Claro!"
    m "({i}Y por primera vez... tengo miedo de sentarme en mi propia cama.{/i})"
    
    scene scene123 with Dissolve(2.0)
    m "({i}Es tan linda. Esto es peligroso.{/i})"
    
    scene scene124 with dissolve
    v "Hola."
    
    scene scene125 with dissolve
    m "Umm... hola."
    m "Te preguntaré directo. ¿Por qué pareces tan cómoda conmigo?"
    
    scene scene126 with dissolve
    v "¿Hmm?"
    m "Bueno, solo nos conocimos hace unos días, y realmente no sabes nada de mí."
    
    scene scene127 with dissolve
    v "¡Es fácil! ¡Te amo!"
    
    scene scene128 with dissolve
    m "¿A-amor?!"
    m "({i}¡Se está acercando mucho!)"
    
    scene scene129 with dissolve
    v "Cuando me salvaste el otro día, mi vida pasó frente a mis ojos."
    
    scene scene130 with dissolve
    v "...y tú estuviste ahí en cada segundo."
    
    scene scene131 with dissolve
    m "({i}Oh, Dios. ¿Está hablando en serio?{/i})"
    m "Me alegra haberte salvado, pero ¿no deberías tener más cuidado?"
    m "No sabes qué tipo de persona podría haber sido."
    m "¿Y si hubiera decidido aprovechar la situación?"
    
    scene scene132 with dissolve
    v "No me molestaría... si fueras tú."
    m "({i}¡Ese cuerpo! ¡Estoy luchando por mi vida aquí!{/i})"
    
    scene scene133 with dissolve
    v "¿Te gusta la vista?"
    
    scene scene134 with dissolve
    m "({i}No puedo negar lo sexy que se ve, pero ¿está bien que haga esto?{/i})"
    m "S-sí. Pero-"
    
    scene scene135 with dissolve
    v "Shh..."
    v "Quiero agradecerte por salvarme. No lo rechaces, ¿ok?"
    
    scene scene136 with dissolve
    m "({i}Joder, no creo que pueda ni aunque quisiera a estas alturas.{/i})"
    
    scene scene137a with Dissolve(2.0)
    pause 1.0
    scene scene137b with Dissolve(2.0)
    pause 1.0
    scene scene137c with Dissolve(2.0)
    pause 1.0
    scene scene137 with Dissolve(2.0)
    m "E-eres muy hermosa, ¿sabes?"
    
    scene scene138 with dissolve
    m "¿Q-qué?"
    
    scene scene139 with dissolve
    m "..."
    m "({i}¡Santo cielo! ¡Son tan suaves!{/i})"
    
    scene scene140 with dissolve
    m "({i}No puedo creer que esté haciendo esto...{/i})"
    
    scene scene141 with dissolve
    m "({i}... pero no creo que pueda contenerme más.{/i})"
    
    scene scene142 with dissolve
    v "E-espera, [name]."
    
    scene scene143 with dissolve
    m "({i}Mierda, ¿la regué?)"
    m "L-lo siento."
    
    scene scene144 with dissolve
    v "No lo estés. Me gusta, pero se supone que te estoy agradeciendo {i}a ti{/i}, ¿recuerdas?"
    
    scene scene145 with dissolve
    m "S-sí, pero realmente no tienes que..."
    
    scene scene146 with dissolve
    v "Solo relájate, ¿vale? Solo siéntate y déjame..."
    
    scene scene147 with dissolve
    v "..."
    
    scene scene148 with dissolve
    v "Dios mío."
    
    scene scene149 with dissolve
    m "¿E-estás bien?"
    
    scene scene150 with dissolve
    v "V-visa preguntarme otra vez cuando termine."
    
    scene scene151 with dissolve
    m "({i}Mierda, solo el calor de su aliento se siente tan bien.{/i})"
    m "({i}No quiero que se esfuerce demasiado-{/i})"
    
    scene scene152 with dissolve
    v "Mmgh."
    m "({i}¡Maldita sea!{/i})"
    
    scene scene153 with dissolve
    m "Eso... se siente bien."
    
    scene scene154 with dissolve
    v "*lame*"
    
    scene scene155 with dissolve
    pause 1.0
    scene scene155b with dissolve
    pause 1.0
    scene scene155 with dissolve
    pause 1.0
    scene scene155b with dissolve
    pause 1.0
    scene scene155 with dissolve
    pause 1.0
    scene scene155b with dissolve
    m "({i}Joder, se siente tan bien...{/i})"
    
    scene scene156 with dissolve
    pause 1.0
    scene scene156b with dissolve
    pause 1.0
    scene scene156 with dissolve
    pause 1.0
    scene scene156b with dissolve
    pause 1.0
    scene scene156 with dissolve
    pause 1.0
    scene scene156b with dissolve
    m "({i}¡Ella es una maldita experta en esto!{/i})"
    
    scene scene157 with dissolve
    m "Te ves tan jodidamente sexy con la boca llena."
    m "No sé cuánto más pueda aguantar."
    
    scene scene158 with dissolve
    v "*respiración agitada*"
    
    scene scene159 with dissolve
    v "No... termines todavía."
    
    scene scene160 with dissolve
    v "Tengo que terminar de agradecerte. Te debo la vida, ¿recuerdas?"
    
    scene scene161 with dissolve
    v "Mi vida... mi cuerpo... es todo tuyo, [name]."
    
    scene scene162 with dissolve
    m "({i}Mierda.{/i})"
    m "Está bien. Lo aceptaré con gusto."
    
    scene scene163 with dissolve
    v "Mmm..."
    
    scene scene164 with dissolve
    v "Voy a hacerte sentir muy feliz."
    
    scene scene165 with dissolve
    v "S-sólo relájate, ¿vale?"
    m "({i}Suena nerviosa, pero no muestra duda alguna.{/i})"
    
    scene scene166 with dissolve
    v "*jadeo*"
    
    scene scene167 with dissolve
    v "*respiración temblorosa*"
    m "¿Estás bien?"
    
    scene scene168 with dissolve
    v "S-sí. ¿Se siente bien?"
    
    scene scene169 with dissolve
    m "Muy bien. Me quieres coger con tantas ganas, ¿eh?"
    
    scene scene170 with dissolve
    v "Sí. P-por favor, déjame coger tu gran polla..."
    
    scene scene171 with dissolve
    m "Está bien, hermosa. Muéstrame cuánto quieres agradecerme."
    
    scene scene172 with dissolve
    v "O-ohhhh..."
    v "¡Siii!"
    
    scene scene173 with dissolve
    m "N-no pares."
    
    scene scene174 with dissolve
    v "T-tu polla me está... volviendo loca."
    pause 1.0
    scene scene175 with dissolve
    pause 1.0
    scene scene174 with dissolve
    pause 1.0
    scene scene175 with dissolve
    pause 1.0
    scene scene174 with dissolve
    pause 1.0
    scene scene175 with dissolve
    pause 1.0
    scene scene174 with dissolve
    pause 1.0
    scene scene175 with dissolve
    pause 1.0
    scene scene174 with dissolve
    pause 1.0
    scene scene175 with dissolve
    m "Estoy... cerca."
    
    scene scene176 with dissolve
    v "[name]... por favor entra."
    v "Por favor... [name[0]]-[name]."
    
    menu:
        "Terminar.":
            jump choice3
    
label choice3:
    scene scene177 with dissolve
    pause 0.5
    show vignette_overlay with dissolve
    pause 0.5
    scene scene177 with dissolve
    pause 0.5
    show vignette_overlay with dissolve
    pause 0.5
    scene scene177 with dissolve
    pause 0.5
    show vignette_overlay with dissolve
    pause 0.5
    scene scene178 with slowdissolve
    v "*chillido*"
    m "¡Joder!"
    
    scene scene179 with slowdissolve
    m "Eres... increíble."
    
    scene scene180 with dissolve
    v "Eso... se sintió tan bien."
    
    scene blank_screen with slowdissolve
    pause 1.0
    show fewminlater at truecenter with slowdissolve
    pause 1.0
    scene scene181 with slowdissolve
    m "({i}¡Esta chica fue una maldita maravilla!{/i})"
    m "({i}Me pregunto si estaría dispuesta a volver pronto.{/i})"
    
    scene scene182 with dissolve
    v "[name]?"
    
    scene scene183 with dissolve
    m "S-sí? ¿Estás bien?"
    
    scene scene184 with dissolve
    v "Me gustaría agradecerte otra vez pronto, ¿vale?"
    
    scene scene185 with dissolve
    m "*se ríe* Claro. Aceptaré con gusto cualquier agradecimiento que me des."
    
    scene blank_screen with Dissolve(4.5)
    show gametitle at truecenter with slowdissolve
    "¡Gracias por jugar! ¡Esperamos que hayas disfrutado!"
    "Si te gustó el juego, por favor considera apoyarnos y revisar nuestros próximos cortos NSFW que vienen pronto."
    "¡Hasta la próxima! ¡Adiós!"
    
    return 