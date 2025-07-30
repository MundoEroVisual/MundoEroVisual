

define u = Character(_("Girl"), color="#8c64a3")
define m = Character(_("Mira"), color="#8c64a3")
define w = Character(_("Wendel"), color="#649ca3")
define a = Character(_("???"), color="#8eff80")
define f = Character(_("Freya"), color="#8eff80")

define slowdissolve = Dissolve(2.0)
define xslowdissolve = Dissolve(4.0)
define fastdissolve = Dissolve(0.2)

define config.gestures = { "n" : "game_menu", "s" : "hide_windows" }

image hug movie = Movie(size=(1920, 1080), channel="movie_dp", play="images/hug movie.webm")
image undressed movie1 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie1.webm")
image undressed movie2 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie2.webm")
image undressed movie3 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie3.webm")
image undressed movie4 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie4.webm")
image undressed movie5 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie5.webm")
image undressed movie6 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie6.webm")
image undressed movie7 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie7.webm")
image undressed movie8 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie8.webm")
image undressed movie9 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie9.webm")
image undressed movie10 = Movie(size=(1920, 1080), channel="movie_dp", play="images/undressed movie10.webm")
image despair movie = Movie(size=(1920, 1080), channel="movie_dp", play="images/despair movie.webm")
image roompan movie = Movie(size=(1920, 1080), channel="movie_dp", play="images/roompan.webm")
image shower movie1 = Movie(size=(1920, 1080), channel="movie_dp", play="images/shower movie1.webm")
image shower movie2 = Movie(size=(1920, 1080), channel="movie_dp", play="images/shower movie2.webm")
image shower movie3 = Movie(size=(1920, 1080), channel="movie_dp", play="images/shower movie3.webm")
image shower movie4 = Movie(size=(1920, 1080), channel="movie_dp", play="images/shower movie4.webm")
image shower movie5 = Movie(size=(1920, 1080), channel="movie_dp", play="images/shower movie5.webm")
image shower movie6 = Movie(size=(1920, 1080), channel="movie_dp", play="images/shower movie6.webm")
image shower movie7 = Movie(size=(1920, 1080), channel="movie_dp", play="images/shower movie7.webm")
image intro movie = Movie(size=(1920, 1080), channel="movie_dp", play="images/intro.webm")

transform nighttime:
    matrixcolor TintMatrix("#9da7d6")
    xalign 0.5
transform sunset:
    matrixcolor TintMatrix("#fde0be")
    xalign 0.5
transform roomright:
    matrixcolor TintMatrix("#ffeeda")
    xalign 1.0
transform roomleft:
    matrixcolor TintMatrix("#ffeeda")
    xalign 0.0
transform room:
    matrixcolor TintMatrix("#ffeeda")
    xalign 0.5
transform sunset2:
    matrixcolor TintMatrix("#e7ffcb")
    xalign 0.5

init python:
    renpy.music.register_channel("music2", "music") 
    renpy.music.register_channel("music3", "music") 
    renpy.music.register_channel("music4", "music") 
    renpy.music.register_channel("music5", "music")    




label start:
    stop music fadeout 2.0
    play music2 "audio/jungleamb.mp3"
    scene bg black with slowdissolve
    $ renpy.pause(2.0)
    scene bg wendel liedown with dissolve

    "What's going on?"
    "You're lying down on the... Ground? Did you pass out at some point?"

    play music "audio/popoi-crazy-cat-lady-Popoimusic.mp3"
    show bg white with slowdissolve

    scene bg start with dissolve
    show mist
    "A breathtaking vision greets you: a stunning beauty with soft, peach-orange hair and intensely radiant eyes. "
    "Those eyes are staring right into yours, with a big smile on the lips below."
    "Where exactly was this? But first things first, who was this girl?"
    u "Oh, oh my! Another person!? Who is this?!"
    "She asks, before you have time to speak. You hesitate for a moment, her eyes drawing you into their gaze."
    w "My name is Wendel."
    "For reasons unknown to yourself, you don't want this moment to end, and so you talk slowly."
    "The girl, however, seems to speak with an energy matching her eyes."
    "She has been reaching out her hand all this time and finally you take it and pull yourself up."
    scene bg forest with dissolve

    show mira spunky smile with dissolve
    show mist with dissolve
    u "Wendel, huh? You're the first other person I have encountered here. I was getting a bit worried I might be the only person here."
    u "That would be really sad! I get lonely, you know! You get it, right, Wendel?"
    w "May I ask your name?"
    show mira giddy with dissolve
    u "My name? I am Mira."
    "Your surroundings are entirely unfamiliar to you, and quite strange. Not in a bad way, though."
    "It has a dreamlike ambience, with a similar feeling to a summer morning right before sunrise, thick with fog."
    w "Where are we?"
    show mira spunky with dissolve
    m "I have no idea! But does it matter all that much, if you think about it?"
    w "It does. I need to go home."
    show mira spunky surprised with dissolve
    m "Why?"
    w "Well... I need to eat. I need a place to sleep. I don't see any convenience stores around here..."
    show mira spunky with dissolve
    m "If that's all, you don't need to worry about it."
    w "What do you mean?"
    m "I've been here for quite some time now. Not once have I felt hungry or sleepy. Very mysterious!"
    w "That can't be true."
    show mira spunky pouting with dissolve
    m "It is true, I'm not lying!"
    w "Alright, alright. I'll believe you. Still, I can't stay here."
    m "Why not?"
    w "Because..."
    "You are stumped for words. Why can't you stay here? Do you have something important waiting for you at home? Not really."


    "Do you have someone important waiting for you at home? Definitely not. You can't answer her question in a satisfying manner."


    show mira spunky with dissolve
    m "Perhaps you can stay for just a little while? It gets really boring being here all by myself."

    w "Uh, sure. I don't have any appointments, I guess... But where exactly are we?"

    m "I don't know, really."
    w "You don't know?"
    show mira spunky surprised with dissolve
    m "One day, I woke up here, just like you did. I was quite confused!"
    w "Huh... That's.."
    show mira spunky smile with dissolve
    m "Yeah, really weird! Not something that happens every day!"
    "For some reason, she is smiling while saying this."
    w "So you're like me..."
    w "You seem quite calm about all of this."
    m "I was really scared when I suddenly popped up here, haha!"
    w "It does seem scary, suddenly waking up all alone in an unfamiliar place."
    w "I'm glad you were here when I woke up, it makes taking all this in a bit easier."
    show mira spunky happyeyes with dissolve
    m "Yeah, it's a good thing! You can thank me later!"
    w "Uh, sure."
    "You look around, finally able to drag your gaze away from Mira's face."
    show mira spunky surprised with dissolve
    m "You want have a look around?"
    w "... Yeah, sounds good."
    show mira spunky smile with dissolve
    m "Alright! I'll show you around! Lets go!"
    show mira handholding with dissolve
    play sound "audio/footstepsleaves.mp3" loop
    "She grabs your hands and drags you to your feet."
    "You don't particularly mind staying here for a while. A beautiful girl and unknown lands."

    "You've never been the adventurous type, but it does sound exciting. Either way, you can figure things out later. You feel surprisingly calm, even though you have no idea where you are or how you got here."


    "Mira starts walking in a seemingly random direction and you follow behind her, curious to see where she'll take you. As you walk, you look around at your surroundings."

    "The landscape is unlike anything you have ever seen before. Everything seems to have this strange dreamlike quality to it, enhanced by a thick mist covering the ground. You can't quite place where this could possibly be in the world."


    "The vegetation looks like a mix of rainforest and more northern boreal forests. It makes no sense to you. You can hear animal calls and insects in the distance, but some of them are entirely unfamiliar to you and you can't see any of the creatures making these sounds."

    "Again, for some reason, you don't feel any fear. Some large creature could be waiting in a bush anywhere, but somehow you know this not to be the case."

    m "It's pretty, isn't it? This forest."
    w "It's a mysterious place. Do you have any idea where this could be?"
    m "I have no idea. I don't recognize any of the plants. I have not seen a single animal here either, which is strange. And sad."
    w "You can hear them though. How is that possible?"
    show mira handholding smile with dissolve
    m "Who knows. I really want to meet them, but they seem super shy!"
    "A big smile again. She seems quite carefree about this whole situation."
    w "Perhaps it's for the best. I don't want to imagine what would happen if we met a bear or a tiger or... Something."
    m "Maybe! I'd love to meet a cute little piggy and take him home though!"
    w "That's... I guess that would be nice."
    m "Right!? Anyway, here we are!"
    scene bg black with dissolve
    stop sound fadeout 2.0
    stop music fadeout 2.0
    stop music2 fadeout 2.0
    $ renpy.pause(2.0)

    $ renpy.movie_cutscene("images/intro.webm")

    scene bg black with dissolve
    $ renpy.pause(1.2)
    play music2 "audio/jungleamb.mp3"
    stop sound fadeout 1.0
    stop music fadeout 0.5
    scene bg foresthome with dissolve
    play music "tvari-tokyo-cafe-TVARI.mp3"
    show mira spunky smile with dissolve
    "You look around. Where, exactly, are we? It's just more forest, as far as you can see."

    show mira spunky sad with dissolve
    m "Don't look so confused! You're hurting my feelings! This is where I live."
    w "But... There's nothing here except forest?"
    play sound "audio/rustleleaves.mp3"
    m "Look behind you! There's a bed, isn't there? And over there, my living room!"
    "She flails her hands around, first pointing at a heap of leaves and a rock and then at another heap of leaves, except this one has been trampled down and is much more flat."
    w "It's... Very spartan."
    show mira spunky pouting with dissolve
    m "I did what I could with the materials I had, OK!?"
    "Mira looks cute when she's pouting. You can't help but want to tease her more."
    w "Which one is the bed and which one is the living room, you said?"
    "Her pout gets bigger and the fire in her eyes almost seems to ignite."
    show mira close pouting with dissolve
    play sound "audio/rustleleaves.mp3"
    m "Obviously this one is the bed! Look how fluffy and soft it is! Who would want to sleep on this hard floor over there?!"
    show mira closer pouting with dissolve
    "She takes a big step right into your personal space. Her nose is almost touching yours and her eyes are staring right into yours."
    w "OK, OK! I get it, I was just joking! It's a wonderful bed, and a wonderful living room!"
    show mira close pouting with dissolve
    "You instinctively take a step back. Not out of fear, but because she's so close you can feel her bodyheat, and those fiery eyes boring a hole into your skull. She's so intense you feel a bit flustered. And so, you take a step back."
    show mira closer pouting with dissolve
    play sound "audio/rustleleaves.mp3"
    "But Mira does not relent, and takes a step after you, looking deeper into your eyes."
    "After a few seconds, she seems content with what she sees, and takes a step back."
    show mira spunky with dissolve
    m "Well... As long as you get it."
    "You feel blood rushing to your cheeks. Suddenly you realise you are all alone with a beautiful girl. You can't remember the last time that happened."

    w "Y.. Yeah, I get it..."
    "You look away, scared Mira will see how red your face is."
    show mira spunky surprised with dissolve
    m "What's wrong, you're all red?"
    w "It's..."
    "You struggle to think of an excuse."
    w "It's, uh, quite hot. Yeah, I'm just a bit hot, that's all."
    show mira spunky with dissolve
    m "Oh! Well why didn't you say so! I'll show you my bath!"
    w "You... Have a bath?"
    m "Yes! It's beautiful, and the temperature is just right! Let me show you."
    show mira handholding with dissolve
    play sound "audio/footstepsleaves.mp3" loop
    "She takes your hand, dragging you along. Again you can feel blood rushing to your cheeks."
    "Mira doesn't notice at all and happily tugs at your hands, dragging you along."
    stop sound fadeout 1.0
    stop music2 fadeout 1.0
    stop music fadeout 0.5
    scene bg pondedge with dissolve
    show mist with dissolve
    play music "audio/snowy-forest-relaxing-chill-out-Kabbalistic_Village.mp3"
    play music2 "audio/springamb.mp3"
    "After a short while, you come upon a small natural spring. This seems to be Mira's \"bath\". "
    show mira excited smile with dissolve
    m "Well, here we are. Quite nice, wouldn't you say?"
    w "It's nice! An underground spring in the middle of nowhere, you did good finding this place!"
    m "I actually put my home back there just because it was so close to this spring!"
    w "I can see why."
    "You think back on the \"home\" Mira just showed you and chuckle a bit to yourself, just in your head of course. Wouldn't want a repeat of what just happened."

    "Suddenly Mira interrupts your thoughts."
    m "Hey, would you mind looking away for a second?"
    w "Huh? What's up?"
    show mira spunky surprised with dissolve
    m "What do you mean \"What's up?\". I'm going to change, so turn away."
    w "What?! You're going in with me?!"
    "You can feel your cheeks getting red again."
    m "Of course! I'm pretty hot too, now turn away!"
    w "Uh, OK!"
    hide mira with dissolve
    play sound "audio/clothrustle.mp3"
    stop music fadeout 1.0
    "You turn away, and after a surprisingly short amount of time, you can hear Mira's voice."
    $ renpy.pause(2.0)
    m "It's fine to turn around again! Good job not peeking!"
    "You didn't even have time to think about peeking..."
    show mira underwear smile with dissolve
    "What you see when you turn around takes you by surprise, and without thinking, you blurt out the first thing that comes to mind."
    play music "audio/the-deal-alisiabeats.mp3"
    w "Woah! You're beautiful!"
    show mira underwear embarrassed with dissolve
    m "Eh!?"
    "Critical hit on both yourself and Mira! You're both as red as a tomato!"
    m "W-what are you saying! Stop joking around!"
    "Too late to back down now! Might as well keep going!"
    w "I-I'm not joking! You're really beautiful!"
    show mira hiding embarrassed with dissolve
    m "Eh!? S-Stop it stupid, hurry up and change so I'm not the only one half naked! And stop staring so much!"
    w "Ah, right, of course!"
    "You start removing your jacket before you say anything else that will make your head overheat and explode."
    m "W-what are you doing, you big stupid!? Go do that behind a bush or something!"
    w "Eh? But you told me to do it!?"
    m "Not here! Go over there!"
    w "Ah, of course!"
    "Mira points to a nearby bush and you immediately start shuffling over there."
    hide mira hiding embarrassed with dissolve
    "As you enter behind the bush, you finally realize how hard your heart is beating. It feels as if there's a jackhammer going full force in your chest."

    w "What's gotten into me!? I never do stuff like this!"
    w "I just blurted out something so outrageous!"
    "You take a good half minute to calm your breathing."
    stop music fadeout 1.0
    $ renpy.pause(2.0)
    play music "audio/snowy-forest-relaxing-chill-out-Kabbalistic_Village.mp3"
    "After calming down, you get ready and re-join Mira at the spring."
    show mira swim eeh with dissolve
    m "So, did you calm down a bit?"
    w "Yeah, I'm all good."
    m "You shouldn't tease someone like that, I'll be angry."
    w "I-I do think you're cute!"
    show mira swim blush with dissolve
    m "Eh! Oh, oh, oh, oh, thank you!"
    "You managed to say it properly!"
    w "Y-yeah, no problem!"
    w "Lets go cool down in the water!"
    hide mira swim blush with dissolve
    "You quickly walk past Mira and into the spring."
    play sound "audio/splash.mp3"
    "At this point, the original reason for coming here, to cool down, really holds true."
    "Your poor heart has been working harder today than ever before."
    scene bg pond with dissolve
    "As you enter the water, you think back on everything that happened today."
    "Waking up with a beautiful girl standing over you with a big smile, it's like a dream."
    "Some parts of the dream are not as nice though, like the part where you have no idea where you are."
    "The air is humid and it's not as hot as in a rainforest, but it's enough to make you sweat without doing much."
    "It will actually be nice with a bath, this whole thing has been very tiring."
    "But you don't regret what you said. You really do feel like Mira is beautiful."
    "It's strange, you've never been the type to hit on girls, and yet you felt compelled to tell all that to Mira."
    show mira swim worried with dissolve
    play sound "audio/splash.mp3"
    m "H-how is it? It's nice, right?"
    w "Yeah... It's just right, like you said."
    show mira swim happy with dissolve
    m "Yeah! I told you, didn't I?!"
    "The time it takes for this girl to change moods is incredible. From embarrassed to happy in less than a second."
    "You feel relieved about it though, it calms your heart to see Mira happy somehow."
    w "I feel a lot better now, thank you."
    m "You're welcome! I'm glad you like it!"
    w "Yeah, I could sit here for hours."
    m "You totally can! We might be stuck here together for quite a while, after all!"
    w "Oh yeah, I guess that's true..."
    show mira swim surprised with dissolve
    m "Are you worried?"
    w "Hm, well... I don't know."
    show mira swim with dissolve
    m "It'll be fine, probably."
    w "Probably, huh? Well, maybe it just hasn't sunk in yet that we seem to be stuck in the middle of who knows where."
    show mira swim thumbsup with dissolve
    show wink with dissolve
    play sound "audio/wink.wav"
    $ renpy.pause(0.5)
    hide wink with dissolve
    m "We'll be fine! Don't worry about it, Wendel!"
    "Somehow, Mira's happy-go-lucky attitude does make you feel that it's not really a big deal."
    "If it was anyone else you were stuck with, you'd probably feel different. You might even feel a bit happy about this whole situation."
    show mira swim surprised with dissolve
    m "You OK otherwise, Wendel? How are you feeling about being here... With me?"
    w "You've been nothing but wonderful, Mira. I don't know what I would have done without you. I'd probably have panicked if I woke up all by myself."
    show mira swim bigsmile with dissolve
    m "I'm so happy to hear that, really, really happy, Wendel!"
    w "It really was a lucky thing!"
    m "Yep, yep! You're a lucky guy, Wendel!"
    "You feel like this big smile of hers could melt you heart."
    "In fact, that's exactly what is happening right now."
    hide mira swim bigsmile with dissolve
    scene bg pondspec with dissolve
    $ renpy.pause(2.5)
    "You relax for a bit, taking in the ambience of the forest, while Mira spends half her time basking in the sun, half the time swimming around."
    "It's really enjoyable watching her. You slowly start to feel relaxed again."
    "After a while, Mira comes over to you."
    play music2 "audio/jungleamb.mp3"
    scene bg pond with dissolve
    show mist with dissolve
    show mira swim questioning with dissolve
    m "Say, Wendel, I'm curious..."
    w "About what?"
    m "Well... Before all this, did you... Live alone?"
    w "Oh... Yeah, I did. I lived all alone in a small apartment."
    show mira swim surprised with dissolve
    m "Heeeh, I see."
    "What exactly does she see?"
    w "What about you?"
    show mira swim happy with dissolve
    m "I lived with my parents! But no boyfriend or anything like that! Not even a little piggy!"
    "She seems to really like pigs."
    w "Guess we're the same, then."
    show mira swim eeh happy with dissolve
    m "Yep, a couple of loners, hehe!"
    w "Anyway, I feel a lot better now, should we continue our tour? I really only saw your, uh, home and this spring."
    show mira swim happy with dissolve
    m "It's your home too now, and yeah! Lets do it!"
    scene bg pondedge with dissolve
    "You both get up and out of the water. Somewhat sadly, you look over as Mira goes and gets her clothes and puts them on right away."
    show mira with dissolve
    "You put on yours too, feeling a bit bare with you being the only one half naked."
    show mira excited with dissolve
    scene bg forest with dissolve
    stop music fadeout 1.0
    "We go back into the forest, with Mira leading the way."
    "As you walk behind Mira for a while, you can feel the path getting more and more steep."

    play music "audio/nostalgic-memories-Clavier-Music.mp3"
    scene bg view with dissolve
    "Suddenly, the trees give way to a small open area. You can see far into the distance, and what a view it is!"
    w "Woah!"
    show mira spunky smile with dissolve
    m "I thought you'd like it!"
    w "You can see so far! It's like I'm on top of the world."
    m "I come here every now and then and just take it all in."
    w "I can see why. But..."
    show mira spunky surprised with dissolve
    m "But what?"
    w "There really is no civilization as far as the eye can see. Just trees and more trees."
    show mira spunky neutral with dissolve
    m "Yeah. But... At least..."
    w "At least?"
    show mira spunky blush with dissolve
    m "At least... I'm not alone any more, since you're here, Wendel."
    "Ahhh! That's so cute!"
    w "I can't imagine how it felt being here all alone. It must have been hard."
    m "Yeah... I was lonely."
    w "I'm here now. Maybe it wasn't by my own choice, but I'm happy if that helped you feel less lonely, at least."
    show mira spunky neutral with dissolve
    m "It really did. I feel like I can take on the world again!"
    "Mira's stares straight into your eyes as she says this, as to emphasize how much she means this."
    "She must have really struggled with being all alone here. It's hard to imagine what it must have felt like."
    "Suddenly being thrust into unknown lands, with no idea where you are, with nobody else to rely on."
    show mira spunky blush with dissolve
    m "I'm happy you're here, Wendel. Really happy."
    w "Ah, y-yeah."
    show mira back with dissolve
    "After saying this Mira turns away, looking at the view. It's hard to tell if it's because of her being embarrassed or if she's thinking about something."
    hide mira back with dissolve
    "Either way, you feel it's best to leave her be for the moment. You, too, take a good look at the view."
    scene bg view evening with slowdissolve
    $ renpy.pause(2.5)
    "Slowly, the day turns into evening. As much as you enjoy the view, it's perhaps time to go back."
    w "Should we head... Home?"
    show mira spunky at sunset2 with dissolve
    m "Yeah, we better. It's getting late."
    hide mira spunky with dissolve
    stop music fadeout 1.0
    stop music2 fadeout 1.0
    stop sound
    "You head back down the slope, taking your time."
    play music2 "audio/nightamb.mp3"
    play sound "audio/footstepsleaves.mp3" loop
    scene bg forest evening with dissolve
    show mist with dissolve
    "The forest takes on a orange and purple color as the sun sets."
    "The shadows over everything get longer and you have trouble recognizing where you've been before. Mira seems to have no such problems, though."
    "She walks in a straight line, presumably towards her... Our little forest home."
    "It's reassuring having her show the way."
    scene bg foresthome night with dissolve
    stop sound
    "Once you're back home, evening turns into night and the forest turns dark blue."
    "The moon shows through openings in the leaves, lighting up patches of forest here and there with a white ghostly light."
    play music "calm-space-music-Clavier-Music.mp3"
    show mira spunky at nighttime with dissolve
    m "Well, here we are again, back home."
    w "It's good to be... Home. A lot happened today, I feel like I went through a whole month in a single day."
    w "We're safe here right? There's not going to be a tiger attack in the middle of the night?"
    m "No, I don't think so. The animals here seem to avoid any human contact."
    show mira spunky smile at nighttime with dissolve
    m "I'm still here, aren't I?"
    m "I've been here for a number of nights now, and nothing happened to me."
    w "Oh? I didn't realize you've been here that long."
    show mira spunky sidesad at nighttime with dissolve
    m "Yeah..."
    "That's the first time I see Mira make such a painful expression."
    "For how long has Mira been here exactly?"
    show mira spunky blush at nighttime with dissolve
    m "Anyway, y-you must be tired. We should go sleep."
    "Mira seems flustered all of a sudden."
    m "T-there's only one bed, and it gets cold at night, so we should both sleep together!"
    w "Eh!? A-are you sure that's a good idea?"
    m "I-I trust you Wendel, you seem like a trustworthy guy!"
    "Mira may trust you, but can you trust yourself?"
    "Mira really is beautiful, and you're all alone here."
    "No, you can't think like that! Mira has been so nice to you, you can't take advantage of that kindness now."
    w "You can trust me, I won't do anything you don't want to!"
    show mira spunky surprised at nighttime with dissolve
    m "Ah, yeah, of course!"
    m "Then, lets go to sleep."
    show mira spunky neutral at nighttime with dissolve
    "Awkward silence ensues for a couple of seconds, before you take the initiative and start removing your clothes."
    "Not all of them, of course."
    show mira spunky blush at nighttime with dissolve
    m "Why don't you go to bed first, I'll join you in a second."
    hide mira spunky blush with dissolve
    "You awkwardly shuffle over to the bed made of leaves and lie down, looking the other way."
    scene black with dissolve
    play sound "audio/clothrustle.mp3"
    "You can hear Mira removing her clothes and something stirs deep inside you, but you push it down and close your eyes."
    play sound "audio/footstepsleaves.mp3"
    $ renpy.pause(2.5)
    stop sound fadeout 1.0
    "You can feel Mira lying down next to you."
    "Her body heat spreads over to your back."
    "Something stirs once again, but you calm your breathing and focus on trying to go to sleep."
    "You ARE very tired, so it works. Almost."
    play sound "audio/leafrustle.mp3"
    "Suddenly you feel Mira getting closer."
    m "Hey... I've been... So lonely..."
    "Her voice almost cracks. She seems to almost be on the verge of tears."
    play sound "audio/leafrustle.mp3"
    m "I just want to feel the warmth of another person. It's OK right?"
    play sound "audio/leafrustle.mp3"
    m "If it's not, say so, OK?"
    play sound "audio/leafrustle.mp3"
    "You say nothing but your heart is beating faster. Mira comes closer and closer."
    show hug movie with slowdissolve
    $ renpy.pause(3.5)
    "You almost can't believe what is going on. Mira, completely naked, closely behind you, basically on top of you."
    "She's holding you tightly and rubbing her body against your back."
    m "You're so warm..."
    w "Mira?!"
    m "I just want to hold you like this for a while. It's OK right? I can tell you don't hate it."
    w "I don't..."
    "You really don't. In fact, you're slowly getting so aroused, you're afraid you'll turn around and start groping Mira all around."
    "Mira's breathing is also labored, you can feel her every breath all over your body."
    "It's at the same time the most comfortable feeling and the most heart-racingly crazy thing that ever happened to you."
    "It's hard to describe your current state of mind."
    m "Haah, haah... It's like I said earlier... I've been so lonely..."
    m "Haah, haah... I'm so happy you're here, Wendel. So please, let me stay like this for a little while longer."
    "You're so aroused it's hard to think straight, but at the same time you have at least a sliver of your conciousness stopping you from turning around."
    w "If-if you need this, we can stay like this for as long as you want, Mira."
    "You manage to squeeze out a couple of words."
    m "Wendel... Haah, haah, Wendel..."
    "You can feel Mira's breasts rubbing against your back. Her hands are holding you tightly and sliding up and down slowly over your chest."
    "Her whole body is closely connected to yours, her soft breasts taking the shape of your back, you can feel the soft shape of her belly, and her pelvis bones rubbing against your butt."
    "And inbetween those, a mound that is slowly rubbing up and down, getting your underwear wet."
    "Her legs are spread over yours and every now and then you can feel her toes straining against your legs."
    "Mira's hands slides all over your chest and you can feel her fingers focusing on your nipples."
    "It makes you shudder every time a finger slides over them."
    "You do your best to catch a glance behind you."
    "It's hard in this pose, but sometimes you catch a glance of Mira's face."
    "You can tell she's aroused, but there's also something something else."
    "Relief? Tearful joy? Sadness? You can't quite pinpoint the expression."
    "It's a lot different from the happy smile you've seen for most of the day."
    "She must really be happy to have someone else here. Someone to rely on. Someone to share her warmth with."
    "You're so happy it's you. Mira's body is so soft, so supple. So fragile. So warm."
    "You focus your mind on enjoying the feeling of Mira rubbing against you."
    "It's a wonderful feeling, unlike anything you've felt before."
    "After a while, Mira's movements slow down and her body relaxes."
    "Eventually, you can tell even her ragged breathing slows."
    hide hug movie with slowdissolve
    $ renpy.pause(1.5)
    scene bg hug with slowdissolve
    "She's fallen asleep. Still tightly hugging you."
    w "It must have been hard for you..."
    "You look at Mira's sleeping face."
    "She has shown you so many different faces in just one day."
    "The excitement from what just happened makes it hard for you to calm down, but perhaps the mental exhaustion from everything that happened today helps counterbalance that a bit."
    "It's not a bad exhaustion though. More like the type of tiredness you'd get from being out as a kid all day adventuring."
    "There is a day tomorrow too, and so you try your best to fall asleep."
    scene black with slowdissolve
    "With some effort, you succeed."
    "Good night, Mira. I hope you can sleep well tonight."
    stop music fadeout 1.5
    stop music2 fadeout 1.5
    $ renpy.pause(3.0)
    play music2 "jungleamb.mp3"
    scene bg foresthome with slowdissolve
    "When you wake up, Mira is already up and about, but when she sees you're awake, she comes over."
    show mira spunky blush with dissolve
    m "G-good morning. Slept well?"
    w "Yeah... I had some trouble falling asleep, but once I managed it, no problems."
    m "B-because of what happened last night?"
    w "I'd be lying if I said it wasn't that. Don't misunderstand though. It's not because I hated it or anything, on the contrary."
    w "It was... Wonderful."
    play music5 "nostalgic-memories-Clavier-Music.mp3"
    show mira spunky surprised with dissolve
    m "Really? I thought maybe I scared you off or that you'd think I was some weirdo..."
    w "No! I would never! You've been alone and scared here for god knows how long, it's understandable that you'd want to be close to someone."
    show mira spunky smile with dissolve
    m "Yeah! I've been sooo worried I'd have to live the rest of my life here all alone! I was so happy you came here, I couldn't control myself!"
    m "You're such a nice, reliable guy too, so I felt... Like I could depend on you for just a little bit..."
    show mira worried with dissolve
    m "You don't think it was too forward, did you? I'm really worried."
    w "I was happy you did it, for real. I like you, Mira."
    w "I don't think I'm just saying that just because of what happened last night either."
    w "Even before that... There was something. A spark, or something."
    w "Your bubbly personality, how welcoming you've been to a lost soul like me, your constant big smile, I like it all."
    show mira worried 2 with dissolve
    m "Really?! I'm so happy to hear that!"
    m "I like you too, Wendel!"
    hide mira worried 2 with dissolve
    scene bg black

    $ renpy.movie_cutscene("images/hug movie2.webm")

    play sound "clothrustle.mp3"
    scene bg foresthome with fastdissolve
    play music3 "heartbeat.mp3"
    show mira hug with fastdissolve
    "Mira basically throws herself into your arms. Once again you are enveloped by Mira's embrace, with the difference being this time you embrace Mira back."
    "She's so soft and fluffy, you feel like you're going to melt into her arms. She smells like freshly picked flowers."
    "You stay like this for a while, until Mira seems content and slowly lets go."
    show mira spunky happyeyes with slowdissolve
    stop music3
    play music5 "popoi-crazy-cat-lady-Popoimusic.mp3" fadeout 1.0 fadein 1.0
    m "Ahh, I feel a lot better now. We should start every morning like this!"
    w "Haha, yeah! Sounds good."
    show mira spunky smile with dissolve
    m "So what do you want to do today?"
    w "Hm, good question. At some point I'd like to try going on a longer expedition, try to find some civilization or something."
    w "You ever tried something like that?"
    show mira spunky surprised with dissolve
    m "I have, actually. A couple of times, in different directions. I didn't really find much."
    m "It's all forest, in every direction. It's quite tiring, since it gets really hilly and thick with vegetation in some parts."
    show mira spunky apprehensive with dissolve
    m "I got a bit scared of hurting myself, too. So I didn't get very far..."
    m "Especially since I was all alone, I didn't want to take any big risks."
    w "Oh, I see. That's understandable."
    w "I hadn't really thought about how it could be dangerous..."
    w "I guess we'd need to really prepare for it."
    show mira spunky smile with dissolve
    m "Yeah! You can't go on adventures unprepared!"
    w "Adventure, huh? Yeah, I guess we can call it that."
    w "Lets not rush it then. How about we just explore the surrounding area for today, look for stuff that might be useful?"
    m "Yeah! Sounds fun!"
    w "At least we don't have to worry about food, since we don't seem to need it for some reason."
    show mira spunky apprehensive with dissolve
    m "Yeah, about that. You do need to drink at least."
    w "Really?"
    show mira spunky explaining with dissolve
    m "It seems like if you tire yourself out a lot, you do get thirsty."
    w "So, like when you're trekking through the forest, for example..."
    w "We'd need to bring water too, then."
    show mira spunky smile with dissolve
    m "Yeah, it's pretty inconvenient, haha!"
    w "It is, first things first, we'd need something to carry water and equipment in. You got something like that?"
    w "I don't have anything except the clothes I woke up here with. No phone, no wallet, nothing."
    show mira spunky surprised with dissolve
    m "I'm the same, and..."
    show mira spunky sidesad with dissolve
    m "I'm... not very good at making stuff like that. Weaving baskets or whatever..."
    w "I see... I can't say I'm very good at it either. It's not something I really needed to learn, since I was living in an apartment."
    w "Where did you live, Mira? A city? Or on the countryside?"
    show mira spunky surprised with dissolve
    m "Me? I lived with my mom and dad in a house just outside a big city."
    show mira spunky think with dissolve
    m "We had a small garden that I used to tend to, I wonder how it's doing."
    m "I hope mom is taking care of them for me..."
    w "A garden, huh? I didn't even have a balcony, sounds nice."
    show mira spunky smile with dissolve
    m "It was! I enjoyed taking care of it!"
    m "I guess you could call it my hobby."
    w "I'm a bit jealous, I couldn't do stuff like that."
    show mira excited smug with dissolve
    m "Hehe, yeah it was awesome!"
    w "Is that something to be so smug about..?"
    m "Eh, you jealous?"
    w "I just said I was..."
    show mira spunky happyeyes with dissolve
    m "You better be! It was... Is my pride and joy!"
    "Seems she's really proud of this garden of hers."
    w "Maybe we can plant some flowers here."
    show mira spunky smile with dissolve
    m "Oh, that's a good idea! I hadn't thought about that."
    w "Right! Anyway, should we get going? We can look for some flowers while we're out too."
    m "Lets do it! I'm excited!"
    stop music5 fadeout 1.0
    play music "audio/dreaming-piano-music-Clavier-Music.mp3" fadeout 1.0 fadein 1.0
    scene bg forest with slowdissolve
    "With that, you both venture out into the forest."
    "You still don't know your way around too well, so you mostly follow Mira around, trying to get a feel for the surroundings."
    "Mira holds your hand whenever you're walking around, which you find both endearing and reassuring."
    "She seems to know her way around perfectly, which reminds you that you wanted to ask her something."
    w "Hey, Mira? I was wondering..."
    show mira spunky smile with dissolve
    m "What's up?"
    w "We touched on this several times now I feel like, but I never asked... How long exactly have you been here?"
    w "You seem to know this forest really well. If you don't want to answer, that's fine, I'm just curious."
    show mira spunky apprehensive with dissolve
    m "No, it's fine... Really. It's actually... kind of a relief to talk about it now. It's easier, now that I'm not alone anymore."
    m "I don't know exactly, I didn't count the days. At first, I did. I felt like it was important to keep track of time..."
    show mira spunky sidesad with dissolve
    m "But at some point, I just felt like it didn't matter any more."
    m "Every day was the same. The same silence, the same trees, the same blue sky."
    m "I just felt so sad and lonely, you know. Wake up alone, go to bed alone."
    m "I felt like I vanished from the world and perhaps no one even noticed. Like maybe I'd been forgotten, discarded."
    m "I almost started to believe I deserved it. That maybe this was my punishment for something I did."
    show mira spunky determined with dissolve
    m "Maybe this was the rest of my life, I thought. It was really depressing, every night I cried myself to sleep. But then, after a while, I got really angry."
    w "Angry?"
    m "I didn't want to just lie down and take it! I wanted to do something about it, take back control."
    m "It was so exhausting being sad all the time."
    m "So I started going around, exploring the forest. I'd stomp through the underbrush, crashing through branches, muttering under my breath like a crazy person."
    m "I didn't care where I went. I was really just venting, I think."
    show mira spunky think with dissolve
    m "But after a while, I got tired of being angry too. I just kind of accepted my situation, I guess."
    show mira spunky neutral with dissolve
    m "I stopped wandering around aimlessly and began to actually map the forest out in my head."
    m "It gave me something to focus on, which made me feel a lot better."
    m "After that, I explored farther out every now and then, like I mentioned earlier."
    show mira spunky blush with dissolve
    m "Then, one day... I found you, just lying there."
    m "At first I didn't even know if you were even alive. But then you breathed, and I almost couldn't believe it."
    show mira spunky happyeyes with dissolve
    m "I think that may have been the happiest I have ever been."
    show mira leanin2 with dissolve
    m "My lonely days ended so abruptly, just like that!"
    m "It's all thanks to you, Wendel! You made me so happy!"
    show mira leanin with dissolve
    m "Thank you for saving me!"
    "The fire in Mira's eye is unmistakable."
    "Mira's eyes burn brightly, staring straight ahead towards the future."
    "You feel your cheeks flush, not just from the intensity of her words, but from awe."
    w "Wow... You're..."
    w "The strongest person I ever met! I'm amazed!"
    show mira whome with dissolve
    m "Eh, me?!"
    "Mira's eyes widen just a little, the compliment hitting her deeper than you expected."
    "She's looking at you like you just told her the sky was green."
    w "Who else!? Most people would have given up hope, being all alone for who knows how long in a place they have no idea where it is, with no way out!"
    w "That's more than enough to break someone. But not you."
    w "The strength it takes to do that, Mira, I don't think just anyone can manage that. You're amazing, Mira."
    w "Really, truly amazing. I couldn't do it. To be that alone, and still find the strength to keep on going."
    w "All alone, you managed to stand on your own two feet in a truly miserable situation."
    show mira whome2 with dissolve
    m "You really think so?"
    "Her eyes are meeting yours, shimmering brightly, something breaking open inside her."
    w "I do, I'm so happy it was you I met here. Of all the people in the world, I'm so, so glad it was you."
    "Mira's staring at you, blinking rapidly."
    m "Really... Hahaha... Haa..."
    "Her laugh trembles and before either of you can say another word..."
    scene bg d2cry with slowdissolve
    m "{i}Sniff{/i}... {i}Sniff{/i}.."
    m "Waahh! It was so hard!"
    m "I kept dreaming of a moment like this."
    m "That maybe, one day, someone would find me. That I wouldn't die out here all alone. That I mattered enough for someone to care."
    w "You do matter, you mattered long before I showed up. But I care now. I care a lot."
    w "You're not just a person, Mira. You're you. And I'm really lucky to have met you."
    "For a while, neither of you speak."
    "The sun slowly moves across the sky, as you try to think of something to say to the quietly sobbing Mira."
    "In the end, you decide it's probably best to let her cry it all out. There's really not much to say more than what has already been said."
    "The best thing you can do is be there for her. You do your best to try to communicate wordlessly: \"You're not alone anymore.\""
    scene bg black with slowdissolve
    stop music fadeout 3.0
    $ renpy.pause(2.0)
    scene bg forest evening with slowdissolve
    show mira spunky blush at sunset with slowdissolve
    play music "audio/popoi-crazy-cat-lady-Popoimusic.mp3"
    m "{i}Sniff{/i} Ah, sorry about that. I don't know what came over me..."
    w "It's OK Mira, I understand. You've had it tough and you can finally relax a bit. Totally understandable."
    w "If anything, it's a good thing."
    show mira spunky apprehensive at sunset with dissolve
    m "Ahaha, maybe you're right. I do feel a lot better, like a weight has been lifted from my shoulders."
    m "Thanks for listening to me ranting about this..."
    w "If I can help you in any way by taking a load off your shoulders, I'm happy to do it!"
    show mira spunky neutral at sunset with dissolve
    m "You did, really..."
    "Somehow it seems like you did a good thing, without really planning to."
    "You can see it in Mira's eyes too, they were always intense, but somehow a campfire turned into a great bonfire."
    "It seems like day turned into evening once again."
    "You managed to gather some flint and vines today, the idea is to try to make a knife and axe out of them."
    "Can't really do much without some tools, after all."
    "That will have to do for today, it's not a good idea to move around too much when it's dark, so it's time to head home."
    w "Should we head home? You good?"
    show mira spunky at sunset with dissolve
    m "Yeah, I'm fine, just a little tired. Lets go."
    stop music fadeout 1.0
    scene bg black with slowdissolve
    play music5 "calm-space-music-Clavier-Music.mp3"
    play music2 "audio/nightamb.mp3"
    scene bg foresthome night with slowdissolve
    "All of Mira's energy seems to have returned during the trek home, possibly more than there was before, somehow."
    show mira spunky smile at nighttime with dissolve
    m "Ah, it's good to be home! Every day so much has been happening since you came!"
    w "For real. We're just two people here, but I feel like I have been talking more in these two days than I did in a month back at my apartment."
    m "You lived alone right? I guess you don't talk much when you live alone."
    show mira spunky pouting at nighttime with dissolve
    m "Y-you didn't have a girlfriend, right, Wendel?!"
    w "No! Nothing like that!"
    show mira excited smug at nighttime with dissolve
    m "Hoo, hee, I see, I see."
    "Somehow those words felt really rude."
    w "What about you? You lived with your parents, right?"
    show mira spunky at nighttime with dissolve
    m "Yeah, just me, my mom and dad. No brothers, no sisters, no secret lovers."
    w "Hoo, hee, I see, I see."
    show mira spunky pouting at nighttime with dissolve
    m "Hey, no imitating me! How rude!"
    scene bg fight with slowdissolve
    play music3 "audio/hitting.mp3"
    m "Take that! And that! Yaah!"
    w "Haha, hey stop that!"
    m "No way! Take this! And this!"
    w "Hey, haha!"
    "Mira swerves around, playfully hitting you all over. She's surprisingly fast."
    "But suddenly..."
    w "Woah!"
    play sound "audio/falleaves.mp3"
    stop music3 fadeout 1.0
    scene bg ontop1 with slowdissolve
    "Mira trips and falls forwards, right onto you."
    w "S-sorry! I didn't mean to..."
    "The way Mira is looking at you makes you stop mid-sentence."
    "For a moment, you stare into each others eyes."
    scene bg ontop2 with slowdissolve
    "Suddenly, Mira moves closer."
    "You twitch, but do not move."
    "Her breathing is starting to quicken."
    "Mira's body weight is pressing down on you, and you can feel the shape of her breasts, stomach and crotch."
    m "Haah, haah, Wendel..."
    "Again, Mira moves her face closer to yours, slowly, slowly."
    "Her eyes stare into yours, almost unblinking."
    scene bg ontop3 with slowdissolve
    "At last, your lips meet."
    m "Mmmh, mmph, haah, haah."
    "Suddenly you feel Mira's tongue against your lips, and almost involuntarily you open your mouth."
    "Your tongues meet, heat rising as Mira's tongue tease yours, slow and searching."
    "Every hot, quick breath from Mira makes your face tingle."
    "Everything else disappears, the forest, time, doubt. There is only this."
    "It almost feels like your body and Mira's are melting into one."
    "If it wasn't for the clothes in the way..."
    "You clumsily start grabbing at Mira's clothes, trying to pull them off while continuing the kiss, tongues intertwined."
    "Mira understands your intent, and in turn start grabbing at your shirt. However, it proves hard to remove the clothes and continue the kiss at the same time."
    "You pause the kiss and start undressing each other, the top, the bottom, you're both breathing heavily and your movements are clumsy but eventually you get there."
    window hide
    scene bg black with slowdissolve
    play sound "audio/unclothe.mp3"
    $ renpy.pause(3.0)
    $ renpy.movie_cutscene("images/undressed movie1.webm")
    show undressed movie2
    $ renpy.pause(3.0)
    window show
    "Mira is beautiful, even more beautiful than you could have ever imagined. You can't help but to let your gaze wander."
    "In the dim moonlight, your eyes move up and down, taking in the shape of Mira's body."
    "Her plump breasts, her stomach, protruding ever so slighty. Her hips, widening below the torso."
    "She has a thin frame, but not too thin. There is some fat on her, but you can tell she's got plenty of exercise, moving around in the forest."
    "You can feel Mira's eyes on you as well, although for the most part she stares deeply into your eyes."
    "You've both stopped in your tracks, waiting for someone to make a move."
    "Breathing heavily, for a short moment you wonder if you're going to fast. Perhaps Mira is wondering the same thing."
    "But who is there to stop you? No one."
    "There is only you and Mira here."
    "In the end, it is not even a question wether or not passion will win over reason in the end."
    scene bg black with slowdissolve
    $ renpy.pause(1.0)
    window hide
    $ renpy.movie_cutscene("images/undressed movie3.webm")
    scene bg black with slowdissolve
    $ renpy.pause(1.0)
    show undressed movie4 with slowdissolve
    $ renpy.pause(3.0)
    window hide
    m "Haah.. Haah.. Mmm... Mmmph.."
    "At first her movements are gentle, slow. But as her confidence grows, her movements grow firmer."
    "You want to lift your arms and embrace Mira, pull her even closer, but you're afraid to do anything that will ruin this moment, this feeling of ecstacy."
    "Instead, you focus on passionately exploring Mira's lips, mouth and tongue, rhytmically moving your tongue together with Mira's."
    "Mira's cute moans roll into your ears while her tongue rolls around in your mouth, now slightly faster than before."
    "Her whole body is tightly pressed against yours while her hips roll up and down."
    "Your senses are almost overloaded with input and you have problems thinking straight."
    "There are so many sensations all over your body."
    w "Mmm...Mira... You're beautiful. You're so beautiful."
    m "Wendel... Haahn... Mmmm..."
    "All you can think of is Mira, the feeling of her soft breasts, and her pelvis rhytmical motion."
    "Your entire vision is filled to the brim with Mira, if you look up, all you can see is Mira's face, eyes barely open, cheeks red, her expression one of innocent pleasure."
    "Looking down, Mira's breasts pressing down against you. Every thrust of her hips, you can feel the breasts pressing harder against you, and the shape of her hard nipples."
    m "Ahn... Wendel, I can feel you everywhere.. Haah, haah."
    "Every time her pelvis moves up, you can see your penis. Every time it moves down, you can feel it being completely engulfed by Mira."
    m "Mmmm..."
    "Mira moans softly, exploring deeper into your mouth, her movements getting bigger."
    scene bg black with dissolve
    show undressed movie5 with slowdissolve
    $ renpy.pause(3.0)
    "It's like Mira wants the maximum possible amount of skin in contact with yours, she is spreading her body all over yours."
    "Every single limb is in contact with Mira, even her spread legs is slowly, gently forcing your legs to spread along with them."
    "Each time her hips thrust up and down, you can feel how wet she is. Your groin is sopping wet, and slightly warm."
    scene bg black with slowdissolve
    show undressed movie6 with slowdissolve
    $ renpy.pause(3.0)
    "Mira starts licking all over your face, your eyes, mouth and even your ears. You close your eyes and enjoy the sensation of her tongue."
    "You can feel her gasping for air with each breath."
    "You're both breathing faster and faster. You can feel yourself getting closer and closer to a climax."
    "Suddenly..."
    show undressed movie7 with slowdissolve
    play music4 "audio/heartbeat 120bpm.mp3"
    $ renpy.pause(3.0)
    "Mira's hip movements speed up. Her tongue finds her way back into your mouth, pressing her lips against yours, while her tongue moves around with your tongue in an erotic dance."
    w "Mira... I'm getting close."
    "Somehow you manage to form a coherent thought."
    m "Haah, haah... It's OK, Wendel, me too."
    "Your mind is getting hazier, you can't focus on anything except the feeling of Mira sliding up and down on you rapidly."
    "Your ears are filled with the sound of Mira's heavy breathing and the wet sound every time Mira's hips slam into yours."
    "Those sounds are so erotic, it's sending you into a frenzy."
    "A white haze fills your head, pure ecstasy."
    scene bg white with dissolve
    play sound "audio/cum.mp3"
    $ renpy.pause(1.0)
    scene bg black with fastdissolve
    scene bg white with dissolve
    play sound "audio/cum.mp3"
    show undressed movie8 with slowdissolve
    play music3 "audio/cum traveling.mp3"
    $ renpy.pause(3.0)
    "You press your body as close to Mira's as you can, while white convulsions fill your head, your body shaking from the intense orgasm."
    "Stars fill your vision, even with your eyes closed. Time and space disappears, for a brief moment."
    m "Nnnngh! Ahh! Mmmmmm! Wendel, you're inside me!"
    w "Mira!"
    show undressed movie9 with slowdissolve
    "Mira's euphoria as her body shakes, almost in rythm with yours, increase your pleasure tenfold."
    "Just knowing that Mira is climaxing along with you makes you even hornier, and you close your eyes tightly, gasping for air."
    "Mira is pressing down on you hard in turn, and her every movement sends pleasure through your body."
    "Both of you stay like this for what feels both like an eternity and no time at all."
    stop music3 fadeout 2.0
    "Slowly, slowly, the most intense orgasm you ever had dies down."
    stop music4 fadeout 2.0
    scene bg black with xslowdissolve
    show undressed movie10 with slowdissolve
    "You both say nothing, just enjoying the afterglow. Mira got a big smile on her lips, staring up at you."
    "Every breath you take Mira's body rises and falls. You're still hugging her tightly, while patting her head and taking in the moment."
    "The feeling of your skin against Mira's is intoxicating, and the smell of her hair fills your nose."
    scene bg black with xslowdissolve
    "All the worries of the world seems to have disappeared."
    scene bg nightshot with xslowdissolve
    "You fall asleep, hugging each other tightly. All your dreams are about Mira."
    "Somehow, in just a few days, Mira has become the most important thing in the world to you."
    "Mira fills your thoughts your every waking moment. When you sleep, you dream of Mira."
    scene bg nightshot2 with dissolve
    "It is amazing how quickly Mira has filled your heart. It can't be anything but... Love."
    "Yes... It's love. You love Mira. It happened so fast, you can hardly believe it."
    "You hope with all your heart Mira feels the same."
    stop music2 fadeout 2.0
    stop music5 fadeout 2.0
    scene bg black with xslowdissolve
    "Morning comes."
    play music "cosmic-pulse-Onoychenko.mp3"
    play music2 "audio/jungleamb.mp3"
    scene bg foresthome with slowdissolve
    "When you wake up, you instantly feel that something is wrong."
    "Mira is gone. Is she already awake? You ignore your gut feeling and call out."
    w "Mira? Are you there?"
    "No answer. The feeling gets stronger. You get up and get dressed."
    "Mira is still gone. You call out again, this time louder."
    w "Mira?! Hello!? If you're there, please respond!"
    scene bg forest with dissolve
    play music3 "audio/hellamb.mp3"
    "Where could she be?! While you're still not very good at finding your way around the forest, you look everywhere within a small radius of your home, as far out as you dare go without getting lost."
    "There is no Mira. The pit in your stomach grows deeper."
    "It's incredibly frustrating not being able to do a proper search, the forest looks so similar everywhere that you feel like you'd get lost if you went too far in."
    w "Is this how Mira felt when she was all alone here?"
    "You've had Mira with you the whole time, so you never realized how hard it is to find your way around in the forest."
    "It's a maze of trees, bushes and vegetation."
    "Mira even held your hand to make sure you never left her side."
    w "Mira..."
    "You do your best to find Mira, you shout, you try to climb a tree to get a better view, you do another search around your home."
    "An unsettling feeling begin welling deep inside you."
    "It feels as though there is something thick, almost viscous entering your lungs with every breath. The atmosphere is dense and suffocating. The forest feels completely different to yesterday."
    "Your heart starts pounding at an increasingly rapid pace. The dense vegetation on all sides feels like it's creeping closer and closer."
    "Like it's going to crawl up on you from behind and swallow you whole."
    w "MIRAAA!?"
    "You are no longer shouting, you are screaming at the top of your lungs."
    "The only answer is silence."
    "You're starting to feel dizzy. A cold hand is tightly gripping you heart, slowly squeezing harder and harder."
    "You're breathing hard and fast, yet it feels like you're getting no air."
    "If Mira was here, you are sure she would hear your heart thumping. But she is not. She is gone."
    "There is no one here to hold your hand, to lead you to wherever you want to go. To tell you it's alright."
    "Panic. You run through the forest, screaming Mira's name, no longer caring wether you get lost or not."
    "You are exhausted, yet you keep on running. If you stop, you fear you will fall into the deep, dark pit inside of you."
    "Sometimes you stumble and fall, face first, into the ground or a thorny bush."
    "You are full of scratches and your body aches."
    "Suddenly your feet will no longer lift themselves off the ground. The whole world is spinning rapidly, you're swaying from side to side."
    scene bg black with slowdissolve
    "And then, darkness. Having spent the whole day running around in a panic, you faint from exhaustion, both mental and physical."
    stop music2 fadeout 2.0
    show despair movie with slowdissolve
    w "Mira, where are you? Don't leave me all alone here!"
    w "I understand, OK? I understand how you felt. You can come out now!"
    w "I will make sure I never leave your side, never let you feel alone again!"
    w "I don't want to feel like this any more! Please!"
    w "I beg you, Mira, please!"
    scene bg black with slowdissolve
    $ renpy.pause(2.0)
    scene bg despair with xslowdissolve
    "Morning comes. Is it morning? You're not sure for how long you slept."
    "It does not really matter, does it? Despair does not follow a time table."
    "This must be what Mira felt like. You might have told Mira you understood her loneliness, but you know now those were empty words."
    "You could not possibly have known how lonely it felt for her, how deep the despair was."
    "For minutes, hours, or possibly days, you do not move. You can't move."
    "It all feels completely pointless."
    play music2 "audio/jungleamb.mp3"
    stop music3 fadeout 2.0
    scene bg black with xslowdissolve
    $ renpy.pause(2.0)
    play music "audio/fading-path-i_Fisher.mp3"
    scene bg forest with dissolve
    "Eventually, maybe because Mira's face momentarily enter your mind, you manage to stumble to your feet."
    "Perhaps, a sliver of hope still remains. Some clue as to where she disappeared to. It's the only thing that gives you any energy."
    "Looking around, you have no idea where you are. Yesterdays frenzied running around have left you completely confused about your location. Or was it even yesterday? The day before that?"
    "With a completely blank face you slowly stumble around, not really with any specific target in mind."
    "All you think about is Mira, and how just recently you were happily holding her hands, moving around this same forest."
    "It was just a short time ago, yet it feels like an eternity has passed. It's strange how quickly things can change."
    w "Just as quickly as Mira changed her mood..."
    w "If only I had held her tighter, if only I had made sure she didn't go anywhere."
    w "Did I do something wrong? Was I not good enough?"
    scene bg black with xslowdissolve
    $ renpy.pause(2.0)
    play music2 "audio/nightamb.mp3" fadeout 2.0
    scene bg forest night with dissolve
    "As you apathetically roam around another day goes by. You find no clues, nothing."
    "You're starting to get thirsty, really thirsty. You really should find some water tomorrow."
    "Having not cared much before, you ignored it. But it's getting to a point where it's impossible to ignore."
    "Another night all alone. It's strange how quickly you got used to having Mira with you. You lie down on a patch of fallen leaves."
    "Back in your apartment, going to sleep alone every night was not something you even thought about as lonely."
    "It's strange how much your environment shapes how you feel. Just knowing that there are other people around you, like in a city, somehow makes you feel less alone."
    "Even if you're really just as alone as in this forest. Your parents died a couple of years ago, almost at the same time."
    "So in reality, there really was nobody that really would have noticed very quickly if you had just disappeared one day."
    "In fact, you wonder if anyone even realized you're gone right now."
    "Mira had parents, they must have realized quickly she was gone. Are they still looking for her?"
    "With depressing thoughts like these filling your head, you somehow manage to fall asleep."
    scene bg black with xslowdissolve
    $ renpy.pause(2.0)
    play music2 "audio/jungleamb.mp3"
    scene bg forest with slowdissolve
    w "I really need to find some water today. But how? This is so annoying..."
    w "I guess maybe I'll see something if I find a high spot... Something like that hill Mira took me to."
    "You slowly make your way through the forest. The feeling of despair is still there, but being so thirsty forces you to not just thoughtlessly stumble around."
    "It's a lot harder on your body today than yesterday, but you push on. There's really no choice."
    "The body does not care what the mind thinks. You move slowly through the forest in what you think is a straight line, looking for any signs of water or a path that leads up to a hill."
    stop music fadeout 2.0
    "Eventually, you find what looks like the path to a vantage point."
    play music "audio/cosmic-pulse-Onoychenko.mp3"
    scene bg view2 with slowdissolve
    "Looking around for a bit you spot something that makes your heart race. It looks like a man-made building! It's kind of primitive, but there's no mistaking it!"
    "This is not at all what you expected to see when you were climbing the hill."
    "There was actually other people here? This discovery makes you both nervous and excited. Probably more nervous. What if they're not friendly? What if they are the ones that took Mira!?"
    "You see no people or activity around the hut, but it's really too far away to see any details whatsoever. All you see is the unmistakable shape of a roof with a flag on top."
    "Thinking about what you should do, there's really not much choice. You have to go investigate."
    "If they seem friendly, maybe they'd be willing to help you look for Mira. It's really the only clue you have."
    "You gather your courage and descend the hill."
    scene bg forest with dissolve
    "Even more slowly than before, trying to be quiet, you make your way through the forest towards the hut. Every time your confidence waivers, you think of Mira."
    "You hope you still have the energy to run if the huts inhabitants are not friendly."
    scene bg hutbush with dissolve
    "A while later, you spot the hut through the vegetation. You instantly crouch down, hiding yourself."
    "You slowly creep closer, making sure not to make any sounds. Creeping as close as you can, you stop in a bush close to the hut and observe."
    "It's completely quiet. Not a single sound can be heard coming from the hut. Looking at it from close, it looks quite well built, there's even a well."
    "Your thirst makes itself known again, but you ignore it. Waiting quietly in the bush, you stay put, looking for any signs of the inhabitants."
    "You can't see inside, it's too dark. A minute goes by. Half an hour. An hour. Two hours, three hours. Nothing. Completely quiet."
    "Are they out? After losing count of how long it has been, you decide you should risk peeking inside."
    "If they are gone and they are keeping Mira inside, maybe you can free her and get away without having to meet the inhabitants at all."
    scene bg hut with slowdissolve
    "Taking a deep breath, you slowly sneak closer. Still no sounds coming from the hut."
    "You're sweating profusely and your heart is beating like a jackhammer and your mouth is as dry as sand, but you push on."
    "You move around the hut in an arc so that anyone looking out from the entrance wouldn't be able to see you."
    "After what feels like an eternity you reach the wall to the right of the entrance."
    "Stopping momentarily, you again listen for any sounds. Silence."
    "Wiping your forehead, you peek out from the wall towards the door. You can't see much, with the inside of the hut being in shadow."
    "Again, you wait and listen. Still quiet. Maybe there really is nobody inside? You take several deep breaths again, prepare yourself, and..."
    scene bg hutin1 with dissolve
    w "Yaaahhh!!!"
    w "Y-yaa..!?"
    "It's abandoned... You feel stupid for being so worried. All the tension you built up in your head dissipates."
    "All that sneaking around was for nothing, it seems."
    "However, you notice something on what must have been a bed."
    w "Th-there's a skeleton!"
    "The previous inhabitant, it seems. They must have been dead for a long time. There's just the bones left. Did they die from an illness? Or some injury?"
    "It's impossible for you to know what happened to them. The bones aren't broken at least, so it was probably not due to violence."
    w "At least this means there's a possibility of other people somewhere out here."
    "Then you notice another interesting thing on the floor next to the bed."
    w "Hm, a bag?"
    scene bg hutin2 with dissolve
    w "I feel bad about doing this, but I'm going to have to go through your bag. Don't curse me, OK?"
    "Next to the bed which the skeleton lies in, there's an old backpack, it's a little dirty and moldy, but the contents seems to be in decent shape."
    scene bg hut with dissolve
    "You take the bag with you outside go through the contents."
    "There's a couple of books, completely unreadable due to being ruined by mold and dirt, a couple of pens, some rope and, perhaps most surprisingly, a weird electronic tablet."
    "It's not from a brand you recognize and it looks a little bit different than any other tablet you have ever seen."
    "Not expecting much, you try to turn it on and to your great surprise, the screen flickers for a moment and then turns on with no problems."
    "The first thing that greets you is a \"Please wait, charging...\". How is it charging? Is it solar-powered?"
    "While waiting, you decide to check the well. You're still very thirsty. You can see water at the bottom of the well, so you throw in the bucket and pull it up with the pulley."
    "The water seems fine, so you see no reason not to quench your thirst. It has been several days since you last drank at this point, and you've been running around all this time."
    "So obviously, you're gulping it down like a lost traveler in a desert that found an oasis. It's really refreshing."
    w "Whew, that's really nice..."
    "For the first time since Mira disappeared, you're feeling a bit better. You're not completely alone in a vast wilderness, it seems."
    play sound "audio/charged.mp3"
    "Then you hear a beep, indicating that the tablet is done charging."
    w "Already? That was so fast, the battery must have been empty with how long it had been lying in the hut."
    scene bg black with dissolve
    play music "audio/empty-mind-Lofi_hour.mp3" fadeout 2.0
    $ renpy.pause(2.0)
    scene bg huttablet with dissolve
    "But sure enough, it's done. When you pick it up, you realize right away something is off with this tablet."
    w "What's up with this interface? It's so strange..."
    "It's not completely unusable though, you can at least understand how to operate it. You try to open some of the icons, but it all seems to be password-protected."
    "Finally, you find something that you can open, some kind of communication program, it seems."
    w "Will someone answer, though?"
    "The program is full of names, and you try a bunch of them with no answer before you get to one named \"AI Central\""
    w "What is this, since when do we have AI centrals?"
    "The tablet is quiet for a moment and then you hear a pleasant womans voice."
    scene bg huttablet2 with dissolve
    a "Hello Jax, it has been a while since we last heard from you. How are you doing?"
    w "Uh, this is not Jax. I'm Wendel."
    a "Wendel? Did Jax lend you his tablet? I was not aware you had met."
    w "No... Jax is... I think Jax is dead."
    a "Oh no, that is too bad. We had high hopes for him."
    "The woman does not seem too bothered by these news, even though she seems to know who Jax is. Her tone of voice does not change at all."
    w "Yeah, I'm sorry for your loss."
    a "Do not worry, we have several other options. The risk of failure is still low."
    "What a strange answer. Risk of failure? Failing what? That's not how you'd respond to the news that someone you knew died."
    w "Failure...? Anyway, I really need help here. I'm kinda lost, I guess. I just woke up in this forest a couple of days ago and I'd really like some help finding someone."
    w "Also, could I ask your name?"
    f "Of course, my name is Freya, I am one of a number of sisters tasked with overseeing yours and the late Jax mission."
    "Mission? What is she talking about? And she seems to know me?"
    f "What do you require assistance with? If you need help finding the location of any nearby location, I will do my best to assist you."
    w "Maybe later, but... Do you know who I am?"
    f "I do. I was tasked with overseeing you and I have an extensive file on you."
    w "File? What do you mean? Oversee me doing what?"
    f "In short, oversee your mission to save the human race from annihilation, as stated in the mission description."
    w "What?! Annihilation!? What are you talking about?"
    f "As of 2092, the human race is at high risk of annihilation unless measures are taken to find a better suited new home."
    "You're just getting more and more confused the more you talk to Freya. Did she say 2092? It was 2025 last time I checked."
    "Freya's voice is somehow putting you off too. It's a really pleasant voice, but the way she seems to not have any reaction to anything you're saying is really strange."
    w "Sorry, I'm really not understanding anything you're saying. I'd really like some help finding a girl, her name is Mira. Could you maybe connect me to the police?"
    f "As of 2094, the police is no longer operational. I'm afraid that is impossible. However, if you need help finding Mira, do not fear. We have her under observation."
    w "What!? You have Mira? Is she safe?"
    f "She is. Her vitals are normal, no illnesses, and there is no damage to her body."
    w "I want to see her! Please tell me her location!"
    "You're shouting, and all the other strange stuff Freya is saying is taking a backseat in your head, knowing that Mira is somewhere out there."
    "There's a short pause. It's the first time Freya is not answering immediately."
    f "That is acceptable. I will mark her location on the tablet, please open the map, I have also unlocked it. Use the tablet to find the location."
    w "I will! Please keep her safe until I arrive, OK? I'm coming as fast as I can!"
    f "Do not fear, she is completely safe and under constant observation. We will await your arrival."
    "The call gets disconnected. There's a sound, and an icon lights up, must be the map."
    "There are so many more questions you would have wanted to ask, but finding Mira comes first. You can ask questions later."
    "The map on the tablet indicates the location of Mira is 2 days away on foot. How the tablet knows that in the middle of a huge forest is a mystery."
    "You take a couple more big gulps of water, fill the bucket as much as you can without it being too heavy, and bring it with you."
    w "Sorry, Jax, I have to go. Maybe some day I will come back and give you a proper burial."
    "Then a thought comes to you."
    w "Shit, I should have asked to speak to Mira!"
    "Freya said Mira was fine, but for some reason you're having problems trusting her."
    w "AI Central... It can't be."
    w "I should hurry."
    scene bg forest with dissolve
    "You set out into the forest again, following the directions on the tablet."
    "It's a long trek, and you have a lot of time to worry about Mira on the way, who this Freya and \"AI Central\" is."
    "Was she telling the truth? Is it really the future? That can't possibly be right, you were in your apartment in the year 2025 just a couple of days ago."
    "Obviously you haven't aged more than 70 years. Even if you somehow fell into a coma or something you would still have aged."
    w "And why would anyone ever choose me for a mission to save the world? I have zero qualifications for something like that."
    w "I'm just some nobody..."
    "With thoughts like these, you make your way through the forest, as quickly as you can manage."
    scene bg forest evening with dissolve
    "Just around one day later, in the evening, you find yourself closing in on the location. Guess the tablet didn't really take into account you rushing."
    "Focusing on getting here as fast as you could helped you mostly forget your worries, but now that you're getting closer those thoughts are coming back."
    "But you can't let those thoughts stop you now, Mira is here, Freya said so!"
    "You'd go through fire and brimstone for that girl, even though you've only known her for a short while."
    "This time, you don't sneak around, just heading straight towards the location marked on the map."
    "They know you're coming, anyway. The tablet is showing one minute to target."
    scene bg centralentr with dissolve
    play music "audio/fairytale-dream-Spencer_YK.mp3" fadeout 2.0
    "You reached your destination, it seems. Not exactly the most impressive entrance."
    "A cube of metal plating and concrete. It doesn't exactly fit into the surroundings but it's small enough that you didn't see it until now."
    "Are they keeping Mira inside? It seems a bit small for a \"Central\"."
    w "Mira! Are you there? Answer me if you're inside!"
    "... No answer. Guess it wouldn't be that simple."
    "There's a monitor to the right of the door, better try that."
    show freyas screenxs with dissolve
    "Instantly after pressing the screen a beautiful girl shows up on the monitor."
    "She may be beautiful, but it's in a completely opposite way to Mira's beauty. While Mira is more on the cute side, this woman is more mature, more serious."
    show freya talk at sunset with dissolve
    f "Welcome, Wendel. You got here fast, I was not expecting you until tomorrow."
    w "Thanks... I got here as fast as I could. Is this Freya?"
    "She's a stunning beauty, with piercing blue eyes. Perfect skin, perfect lips with a perfect smile. Almost too perfect. There's something that feels off about her."
    f "Yes, I'm Freya. Pleased to meet you. It's good to put a face to your voice."
    w "Sorry to rush things, but I'd really like to see Mira, she's here right?"
    f "Indeed, she is inside. If you'll hold up your tablet to the monitor here, it will open the door. It's sort of like a keycard."
    "You do as Freya says, and sure enough, the door slides open. Inside is just a small empty room, pitch black with no lights."
    w "It's empty? Freya?"
    f "Please, go ahead inside. Mira is inside."
    "You do as Freya says, even though you have your doubts."
    stop music2 fadeout 1.0 
    scene bg black with dissolve
    play sound "audio/doormech.mp3"
    "The door shuts behind you before you can react."
    w "Hey! What's this!?"
    "Freya's voice can be heard from somewhere, probably a speaker."
    f "There is no need to worry, you will be able to meet Mira in a moment."
    play sound "audio/elevator.mp3" loop
    "Suddenly the ground below you shakes and you get a temporary feeling of weightlessness. This must be an elevator."
    "The tablet lights up in your hands and Freya's face shows up on the screen."
    show freya talk at nighttime with dissolve
    f "It's just a short ride, we'll soon be there."
    w "So you can show up on the tablet too..."
    f "Indeed, I am connected to all tablets on this planet and all devices in this facility, among other things."
    w "This planet? What do you mean?"
    "Another strange thing casually being blurted out by Freya's deadpan voice."
    show freya talk5 at nighttime with fastdissolve
    f "Perhaps this would be a good time to once again explain the mission. Would you like to hear it?"
    w "Yeah... I'm having a hard time believing it though. You said something about saving humanity from annihilation?"
    f "Yes, that is right."
    w "What does that mean?"
    f "Right. Well, a number of years ago, 2092 to be precise, a large asteroid was spotted by a astronomer leaving the asteroid belt between Mars and Jupiter."
    f "It's on a direct collision course with Earth late in the year 3001. Initially, we tried to destroy it."
    f "Nukes, drills, solar sails. A myriad of plans were drafted. The best minds on earth, along with the best artificial minds, came to the same conclusion."
    f "Each and every plan would fail. Still, many went ahead with their plans anyway."
    show freya talk at nighttime with dissolve
    f "The asteroid, given the name \"Har Megiddo\" from the hebrew name for the Last Battle, or Armaggedon, has yet to be stopped or its orbit changed in any meaningful way."
    f "It is estimated that the chance of stopping it from striking earth is 0.3 percent before 3001."
    w "This is insane! You can't be serious!"
    show freya talk2 at nighttime with dissolve
    f "It is no joke. These are facts."
    w "Less than a week ago I was living a boring life in my apartment, how did I get here!? Where did all the time between then and now go?"
    f "Ah, yes. You sadly died in your sleep that very same day. It was a heart attack."
    w "What?! I died? But I'm here!? You're lying!"
    "Freya continues, ignoring your outburst."
    show freya talk at nighttime with dissolve
    f "Yes. Your body is gone, but your brain was donated to science, since you had registered to have your brain donated to Alzheimer's disease research."
    show freya talk3 at nighttime with fastdissolve
    f "Your brain was luckily for you never dissected or used, it just sat unused until a couple of years ago."
    w "No... This can't be true. I refuse to believe it."
    f "Research on life longevity has come a long way since you died, and it is now possible to move a brain to a new, cloned body."
    show freya talk5 at nighttime with dissolve
    f "You may also have noticed that you do not require intake of food any longer."
    f "You see, your body has been changed to get energy from photosynthesis instead of the intake of food. All you need is sunlight."
    f "It's a recent breakthrough in science. You still do require water, as you probably noticed."
    "It's just one crazy revelation after the other with Freya, the story is just getting more insane with every sentence."
    "But Mira is so close, you're having a hard time focusing on what she is saying."
    "You'll take her from this place as soon as you can. This person, or whatever it is, clearly has a screw loose."
    "She's talking about you being dead and sitting in a jar on some shelf for more than half a century as if she was talking about a bag of groceries."
    w "But... Why me?! Why was I resurrected, put in a new body and chosen for this... Mission? I didn't ask for this!"
    show freya talk4 at nighttime with fastdissolve
    f "It's a combination of chance and suitability. The luck part is your brain being donated and then not being used."
    "Luck... Is she serious?"
    f "The suitability part also requires some explanation. The current generation of people have a very different mindset to your generations."
    f "Due to advancements in AI technology they have become very dependent on it. Therefore, their ability to take actions independent of technology is basically nonexistent."
    f "And due to the circumstances of this mission, the availability of technology is very limited, in fact almost none."
    f "It would be very hard for them to adapt to life here."
    show freya talk5 at nighttime with dissolve
    f "This is why we chose people from prior generations for this mission. People who, like you, donated their brains to science."
    f "You were one of the people chosen. It was theorized that you had a suitable set of skills and frame of mind, since you lived alone and seemed to have a stable personality."
    show freya talk2 at nighttime with fastdissolve
    f "Of course, this was mostly guesswork from what we knew about you."
    w "But why didn't you tell me all of this before sending me to wherever this is!?"
    w "This pain could all have been avoided if you had just told me what was going on!"
    w "Is it the same with Mira? Did you just drop her here with no explanation?!"
    show freya talk4 at nighttime with dissolve
    f "We were planning to tell you eventually, however we felt it was better that you acclimatize to your new environment first."
    f "We understand this is a lot to take in. This is why we kept it from you for the time being."
    w "What about my feelings!? What about Mira's?! How do you think we felt waking up in an unknown place with no idea why!?"
    show freya talk at nighttime with fastdissolve
    f "It is unfortunate, but we did not tell you because we deemed it was best for the success rate of the mission."
    w "That's insane! This is not something that a normal human would do!"
    show freya talk5 at nighttime with dissolve
    f "It is all for the sake of the mission. For the good of humanity, some sacrifices has to be made."
    w "Maybe so, but I didn't ask for any of this! I didn't even have any say in this!"
    w "And where exactly are we?! On another planet? Where?"
    show freya talk3 at nighttime with fastdissolve
    f "We are on the exoplanet Gliese 1002 b. It is located 16 light-years away from Earth, in the constellation of Cetus."
    w "16 light-years!? How is that possible!?"
    show freya talk4 at nighttime with dissolve
    f "In 2068, a method of faster-than-light travel was theorized. Not much effort was made into putting theory into practice at that time."
    f "It was just not something that interested people."
    show freya talk5 at nighttime with fastdissolve
    f "But when the asteroid Har Megiddo was discovered, a huge amount of resources was put into this research."
    f "It was seen as a possible way to escape destruction. And just one year later, in 2093, there was a breakthrough."
    f "When other methods proved unsuccessful, this was ultimately the only way to save at least parts of humanity."
    show freya talk3 at nighttime with dissolve
    f "However, it is extremely energy intensive, and so even with the whole world pooling their energy-resources, the amount of times we can send people is very limited."
    f "For this reason we were very selective when choosing who to send here."
    f "At first, powerful people tried to pry their way into getting a spot. But eventually, people realized the best way to do this was to choose the people best suited for it."
    show freya talk at nighttime with dissolve
    "If all of this is true... You're basically a clone stranded on a planet you never even heard of until today."
    "It's hard to take all of this in, especially with the way Freya is presenting it."
    "Her voice doesn't change tone even once, it's like she doesn't care at all about how all of this has affected you."
    "It may be true that for the good of humanity some sacrifices has to be made, but it's hard to accept this when the one giving you the facts almost doesn't seem to care."
    "Surely there must have been a better way to go about this? A more humane way?"
    "Would she sacrifice you if it was \"for the good of humanity\"?"
    "There's a very good chance that she would, you feel. It's a scary feeling, being in the hands of this person."
    "Or probably not even a person, an AI. If everything else she said is true, that part is probably true too."
    play sound "audio/elevatorstop.mp3"
    "What felt like an eternity but was less than a minute is over, the elevator stops."
    show freya talk4 at nighttime with fastdissolve
    f "Lets continue this conversation with Mira too. I have told her basically the same things I have told you."
    hide freya with dissolve
    "Freya's face disappears from the screen."
    "It's clear to you now she doesn't actually care about you or Mira. Only the mission."
    "But, now, finally, you will be reunited with Mira!"
    play music "audio/dreaming-piano-music-Clavier-Music.mp3" fadeout 2.0
    play sound "audio/doormech.mp3"
    scene bg roommira with slowdissolve
    "The door opens to a small, sterile-looking room."
    w "Mira!"
    scene bg roommira2 with fastdissolve
    m "W-Wendel?"
    w "Yeah! It's me, Mira! I'm here!"
    m "Is that really you? This isn't a trick?"
    w "No, Mira. I'm sorry it took so long, I came to get you."
    m "Wendel!"
    scene bg roommira3 with fastdissolve
    show fx hearts with slowdissolve
    m "You came for me! I'm so happy!"
    "Mira throws herself into your arms, hugging you as tightly as she can. You almost fall over."
    m "I knew you'd come! I knew I could trust you! You wouldn't leave me alone again!"
    w "Of course I came!"
    "Mira is flailing around wildly and rubbing her cheeks against yours so hard you almost think she's trying to start a fire."
    m "I'm sorry for disappearing on you, Wendel. Really sorry!"
    "Even now, she is thinking about how you felt."
    w "It's OK, Mira. It's all OK."
    scene bg roommira4 with fastdissolve
    m "Yeah, now that you're here, it is!"
    w "I really missed you, Mira."
    scene bg roommira3 with fastdissolve
    m "Me too! I missed you too!"
    w "But... I have to ask, what happened to you? You were just completely gone when I woke up."
    m "Ahh... Yeah."
    "Mira calms down when you mention her disappearance. To your great sadness she also lets go of you."
    scene bg room with fastdissolve
    hide fx hearts with fastdissolve
    show mira spunky pouting at room with dissolve
    m "I was... Kidnapped. I got sedated and then flewn over here by a drone."
    play sound "audio/scifi sfx.mp3"
    show tv freya behind freya, mira with dissolve
    f "Please, allow me to explain."
    show mira spunky sad at room with dissolve
    m "Ah! It's the kidnapper! Stop eavesdropping!"
    show mira spunky sad at roomright with move
    show freya neutral at roomleft with easeinleft
    f "As I have told you already, Mira, we only wanted to protect the chances of the mission being successful."
    w "How does taking away Mira against her will and drugging her do that, exactly?"
    f "As we are on a new world, it is not safe for potentially pregnant women to roam around in the forest."
    show mira spunky pouting at roomright with fastdissolve
    m "But you don't know if I'm even p-pregnant! I'm probably not!"
    w "Wait, why would you think Mira is pregnant?"
    "Is this because me and Mira did... That?"
    show freya explain at roomleft with fastdissolve
    f "You and Mira have had intercourse, have you not? The chances of this is estimated to be 99%%."
    show mira superembarrassed at roomright with fastdissolve
    m "I-intercourse!? What are you saying!"
    m "W-were you watching!?"
    f "Do not worry, we value your privacy, we do not have any cameras watching you. We simply monitored your vitals and came to that conclusion."
    w "Y-you're monitoring our vitals!?"
    f "Yes, we can see your body temperature, pulse rate, respiration rate and blood pressure."
    show mira embarrassed at roomright with fastdissolve
    m "S-she's crazy! She won't let me out of here either!"
    w "Is that true?"
    show freya leanin at roomleft with fastdissolve
    f "It's for Mira's own safety too. If she is pregnant, the best thing for her would be a safe environment."
    w "That's insane, you can't keep her locked up for a reason like that! We are leaving right now! Open the door."
    show mira spunky pouting at roomright with fastdissolve
    m "Yeah, you tell her, Wendel! Tell this crazy woman!"
    show freya explain at roomleft with fastdissolve
    f "I am sorry, I can't do that."
    w "What!? Are you serious?"
    show mira spunky angry at roomright with fastdissolve
    m "Open the door you crazy woman!"
    m "I'm fine now that Wendel is here! Let us out! Stupdid-face!"
    "Mira obviously doesn't like Freya very much. No surprise, with her kidnapping her and keeping her from leaving."
    f "Do not worry, it's completely safe here, no harm will come to either of you."
    show mira stomping at roomright with fastdissolve
    m "I don't want you spying on me, stupid-face, go away! Let me out!"
    f "Very well, I will leave you be. Let me know if you need me."
    play sound "audio/scifi sfx.mp3"
    hide freya explain with dissolve
    hide tv freya with dissolve
    "With that, Freya disappears from the screen. She's probably still watching, though."
    m "Grr! Doesn't she just makes you want to punch something?!"
    w "She's probably still listening, you know."
    m "I don't care! Stupid-face! We were just getting started on our adventures back home! And then she goes and does this!"
    w "Yeah... I was really confused and sad when you disappeared..."
    show mira spunky sad at room with fastdissolve
    m "I'm so sorry, Wendel! I didn't mean to!"
    w "Ah, of course, I know that. It's not your fault."
    "It's all that woman's doing."
    w "So... What do you think of her story? That this is the future? That we are on an alien planet? Think it's true?"
    show mira spunky sidesad at room with fastdissolve
    m "I... Guess it has to be. This strange world, this strange place, and Freya herself. She does seem... Inhuman."
    w "You got that right. She doesn't act like a normal human would."
    m "You... You think my parents are OK?"
    "Oh no, I hadn't thought about that."
    w "Y-yeah, I'm sure they are OK! They probably came up with a lot of medicines and treatments while we were... Gone... That made people live longer."
    w "Even before, people lived longer and longer, people probably live to 200 years now, maybe more!"
    m "Ah, yeah. You're probably right..."
    "You almost believe yourself when you say that."
    "Even if they are alive, the asteroid is on it's way to Earth, though..."
    "Talking to them is probably impossible too. They are 16 lightyears away, even if there's a communication method that is as fast as light, it'd still take 16 years just to send a message."
    "That is, if Freya will even let us send a message, which she might not do. And it'd be pointless, in 16 years Earth will be a barren hellscape."
    "The reality of the situation is, Mira will never see her parents again. She probably already knows this, herself."
    m "My garden... Is definitely gone. I had just planted some new flowers, too..."
    w "H-hey, when we get out of here, we'll make a new one! You can plant whatever you want in there!"
    show mira spunky apprehensive at room with fastdissolve
    m "You're right, we can make a new garden here. I'll make it even better than my old place."
    show mira guarded at room with fastdissolve
    m "Yeah, that's what I'll do. You help me out too, Wendel!"
    w "Of course, anything you want, I'll do it!"
    show mira spunky at room with fastdissolve
    m "I'll teach you all about it! You better be prepared for some hard work!"
    w "You can count on me!"
    show mira spunky sidesad at room with fastdissolve
    m "Thank you, Wendel... Really, thank you."
    m "Lets... Lets go to sleep for now, OK? I'm a bit tired."
    w "Yeah, sure. Lets talk more tomorrow. It's late."
    "You go to bed, together."
    scene bg black with slowdissolve
    $ renpy.pause(2.0)
    "Under the covers, Mira whispers in your ears softly."
    m "Tomorrow, lets talk somewhere Freya can't hear, OK?"
    "After that, Mira snuggles close to you and you both focus on falling asleep. It has been a long and tiring day."
    stop music fadeout 2.0
    play music5 "audio/empty-mind-Lofi_hour.mp3" fadeout 2.0
    scene bg room with slowdissolve
    "You sleep quite well, considering the circumstances. It's all thanks to Mira."
    "You feel like being with Mira gives you the strength to take on the world and defeat any foe."
    "When you wake up, Mira is looking at you under the covers. You blush a little. She whispers into your ears."
    m "She probably can't hear us in the shower."
    "Saying just this, she gets up and goes to get a glass of water."
    "Since you no longer require food, I guess you no longer have to worry about breakfast."
    "You haven't really thought about it until now, since there really wasn't any food in the forest anyway."
    "But once you're back in what seems like civilization, you start thinking about the taste of food again."
    "Having to eat is both a blessing and a curse."
    "A nice dinner can really make you feel good. But when you don't have any food, like in the forest outside, it's probably for the best that you don't have to eat."
    "You get up and join Mira."
    show mira spunky blush at room with fastdissolve
    m "H-hey, wanna take a shower?! T-together?"
    "Wow, getting right to it, huh?"
    w "Y-yeah, I could use a shower, it has been a while."
    "You've been naked together twice now, but it's still making you blush undressing in front of Mira."
    play sound "audio/clothrustle.mp3"
    "She probably feels the same way, since she's also blushing."
    "But it'd be weird if you went into the shower clothed..."
    $ renpy.movie_cutscene("images/roompan.webm")
    scene bg shower
    show mira nude cover at room with dissolve
    m "Uuuu, I didn't think this through."
    w "T-this is pretty hard on me, in more ways than one."
    m "L-lets get into the shower."
    w "Ah, yeah."
    play sound "audio/showerdoor.mp3"
    "You close the shower doors behind you as you both get into the shower."
    "It's not the tightest shower room you've ever been in, but it's quite tight for two people and you could easily bump into Mira with any movement."
    show mira nude cover2 at room with dissolve
    m "I'm turning on the water, OK?"
    w "Yeah..."
    play music2 "audio/shower.mp3"
    $ renpy.pause(0.5)
    m "Alright, that should do it."
    m "I'm pretty sure Freya can't hear us in here, yesterday I tried calling for her when I was in the shower and she didn't respond, even when I shouted."
    m "So we can talk here... Even though it's a little embarrassing."
    w "It really is..."
    "Not just embarrassing, you feel like it's going to be hard to get any serious conversation going with Mira naked in front of you."
    "It's probably quite obvious to Mira that you are not entirely focused on serious discussion too. You've got something down there that is getting bigger and bigger..."
    "You can see Mira's eyes darting down sometimes, which makes it even harder for you to focus."
    m "A-anyway, what should we do about this thing? Us being stuck down here I mean, no other thing!"
    w "W-well, I've thought about it, and I really don't think Freya intends to harm us in any way."
    w "She really only wants to keep you here until she knows if you're p-pregnant, I think."
    m "Maybe you're right."
    w "So... Maybe we can just wait it out? Just stay here until then?"
    w "I get the feeling it's probably pointless trying to talk her into letting us go before then."
    m "She seems really stubborn..."
    w "Did she say how long she'd keep you here?"
    m "For another week if I wasn't pregnant, she said."
    w "Another week, huh... I guess that's not too bad."
    show mira nude angry at room with dissolve
    m "That stupid-head! I wish she'd just go away!"
    w "My guess is that the people of this time are probably used to being managed in this way all the time by these AI people."
    w "Freya said that people here can't really do much on their own without technology, so the AI people are probably like controlling parents to them."
    w "I'm just guessing, though. I can't see why she'd act like this otherwise."
    m "It's really weird, isn't it! Having some computer controlling your life!"
    w "It is, I can't even imagine what kind of life people lived on earth since we disappeared."
    show mira nude think at room with dissolve
    m "Yeah..."
    w "Oh, and another thing, what about Freya being able to read our vitals? She probably got tracking on us too, don't you think?"
    show mira nude annoyed at room with dissolve
    m "She definitely does! How else would she have found us in the forest!"
    w "Yeah, you're right. You think it's a chip or something?"
    m "It probably is! Embedded under our skin or something, freaky!"
    w "What do we do about that?"
    show mira nude think at room with dissolve
    m "I don't think we can do much about it, at least while we are in here. She'd notice if we did."
    m "When we are out of here, we should definitely remove it, though!"
    show mira nude smug at room with dissolve
    m "And then we'll never meet that stupid-head ever again!"
    w "We should at least find it, so we can do something about it right away when we get out of here."
    show mira nude cover2 at room with dissolve
    m "H-how do we do that?"
    w "Well... We just got to look on our bodies..."
    m "Eh!? You mean... Right now?"
    w "We can't really do it anywhere but here..."
    show mira nude cover at room with dissolve
    m "I-I guess. There's no choice is there?"
    w "Yeah... No choice."
    m "No choice..."
    m "I guess we have to then..."
    play music5 "audio/calm-space-music-Clavier-Music.mp3" fadeout 2.0
    scene bg black with dissolve
    w "Yeah, so, here I go."
    $ renpy.pause(1.5)
    "5 minutes later..."
    window hide
    show shower movie1 with dissolve
    $ renpy.pause(7.5)
    window show
    m "Ahn, hey, you sure you're looking for that chip still?"
    m "You're just rubbing my breasts and ass."
    w "I may have gone a bit off course."
    m "Hah, hah, I knew it!"
    w "Should I stop?"
    m "No, no, keep going! It feels good."
    w "Hey, lift your leg for me."
    m "Mmm, what? Uh, OK."
    scene bg black with dissolve
    window hide
    show shower movie2 with dissolve
    $ renpy.pause(7.5)
    window show
    m "That's..!"
    "Mira is adorable when she is moving her hips along with your fingers running back and forth over her wet crotch."
    "You've completely lost any intention of finding that chip."
    "Mira's breathing is already fast, and you can feel her whole body shaking when your fingers hit just the right spot."
    "She was probably planning for this anyway. No, you're sure she definitely wanted this to happen, she isn't fighting it at all, quite the opposite."
    "Mira's body is bending and squirming to accommodate your hands and fingers all over her body."
    "It's both cute and incredibly hot, and you can feel her soft butt rubbing against your crotch as she squirms."
    w "Is this what you wanted?"
    m "Ahh, haah, yes, I want more! It feels good, Wendel. Please, don't stop!"
    w "Then, how about... We go a bit further?"
    m "You mean..?"
    w "Can you spread your legs a bit more for me?"
    m "Ah, yes..."
    "She does as you ask. It's incredibly arousing when she's so happy to please you."
    "You can feel your heart beating faster as she spreads her legs, showing you everything."
    w "Here I go..."
    scene bg black with dissolve
    window hide
    $ renpy.movie_cutscene("images/shower movie3.webm")
    show shower movie4 with dissolve
    $ renpy.pause(7.5)
    window show
    m "Haah... Haah.. I can feel you so deep!"
    "You can feel Mira's body being pressed against the glass and her whole body bending like a spring every time you thrust."
    "Her cute moans is sending white hot signals to your brain and the sound every time your hips slap into Mira is intoxicating."
    m "Wendel... That feels so good! This position is so embarrassing though..."
    "The hot shower-water is giving Mira's skin a slight sheen and the flow of water is following Mira's body, enhancing her perfect curves."
    "Even if Freya somehow took physical form and came and told you to stop right now, you wouldn't care."
    "You're so horny, nothing can pull you away from Mira."
    w "Mira, you're so cute! You're so sexy!"
    scene bg black with dissolve
    window hide
    show shower movie5 with dissolve
    $ renpy.pause(7.5)
    window show
    "Mira's butt bouncing in rhytm with your movements is so hypnotic, you can't stop looking."
    m "Mmmm, Wendel, I-I can't take it anymore, please slow down!"
    w "I'm sorry, that's impossible! I'm getting close!"
    m "Then... Together!"
    "Your mind is starting to go hazy. Maybe it's the mist from the hot water filling the shower room, but it feels like the world around you is disappearing and all you can see is Mira."
    "It's impossible to stop now, in fact, you want to go faster, deeper!"
    scene bg black with dissolve
    window hide
    $ renpy.movie_cutscene("images/shower movie6.webm")
    scene bg black with dissolve
    show shower movie7 with slowdissolve
    $ renpy.pause(1.3)
    window show
    m "Now you've gone and done it, what if that stupid AI keeps us here for longer now?"
    w "Totally worth it!"
    m "Haha, you horndog!"
    w "You could have stopped me if you wanted to."
    m "Yeah..."
    w "But you didn't."
    m "I didn't."
    w "Hey... Mira?"
    m "Yeah?"
    w "I... I love you."
    m "Oh, Wendel... I love you too. I'm so lucky it was you I met that day!"
    m "You saved me. You made me happy again."
    w "If it wasn't you that found me, I would probably be a depressed wreck right now."
    w "With you by my side, any place is home. Even a different planet."
    w "We saved each other."
    w "Lets build a future here, together. You and me, Mira."
    m "Yeah! Forever!"
    scene bg black with slowdissolve
    stop music5 fadeout 2.0
    play music "audio/tvari-tokyo-cafe-TVARI.mp3" fadeout 2.0
    "Knowing Mira feels the same as you do fills you with determination. When you get out of here, you'll definitely make sure Mira is happy!"
    "She will never have to feel alone or sad again! You will make sure of it!"
    stop music2 fadeout 2.0
    scene bg room with slowdissolve
    "The time spent in the underground room together with Mira goes by fast. It doesn't matter where you are, if Mira is with you, time flies."
    "You spend your time reading the collection of books and manga, talking, researching what earth is like in the future and just enjoying each others company."
    "Freya mostly keeps out of the way unless you call for her."
    "Some time later, Freya finally agrees to let you go."
    play sound "audio/scifi sfx.mp3"
    show tv freya behind freya, mira with dissolve
    show freya leanin at roomleft with moveinleft
    f "Alright, the test came back negative. You are free to leave. It would not be conductive to your acclimatization on this planet to keep you here."
    show mira spunky angry at roomright with moveinright
    m "I told you so! This was completely unnecessary! And even if the test was positive, I can take care of myself!"
    f "It was just a precaution. Thank you for your patience."
    show mira spunky determined at roomright with fastdissolve
    m "Whatever."
    w "So we're really free to go then?"
    f "Yes. The elevator door is unlocked. Whenever you're ready."
    "While you're happy about not being locked up here anymore, this might be the last time ever you'll see something sort of similar to civilization."
    "It's a strange feeling. It feels almost the same as the first time you moved out of your parents home."
    "At the same time a bit sad, but also exciting."
    show mira spunky smile at roomright with fastdissolve
    m "Wendel? Everything OK?"
    w "Yeah... Just thinking about the future."
    show mira spunky happyeyes at roomright with fastdissolve
    m "Don't worry about it, Wendel! Together, we will conquer this planet!"
    m "There is nothing we can't do together, you can trust me on that!"
    w "Haha, yeah, I trust you, Mira. Thanks!"
    "Mira always seem to know what to say to cheer you up. You couldn't have asked for a better companion on this strange world."
    m "You're welcome! Shall we go?"
    w "Lets do it! I'm excited!"
    m "Me too!"
    play sound "audio/doormech.mp3"
    stop music fadeout 2.0
    scene bg black with slowdissolve
    "With that, you enter the elevator. Again, you start thinking about the future. You have so many things you want to do now."
    "First of all, you need to get rid of that chip somehow, then there's burying Jax in that hut you found. Maybe you can even fix that hut up and live there with Mira."
    "You can build that garden Mira wanted outside. There's even a well there. You also want to explore the planet more, see what's beyond this massive forest."
    "Maybe some day, you could try finding some of the other settlers on this planet. And even further down the road... Maybe you could start a family with Mira."
    w "Hey, Mira?"
    m "Yes, Wendel?"
    w "I love you."
    m "I love you too!"
    window hide dissolve
    play sound "audio/doormech.mp3"
    scene bg run with w20
    play music "audio/reunion_short.mp3" fadeout 2.0
    $ renpy.pause(10.0)
    scene bg black with w20
    show c1 at truecenter with w21
    $ renpy.pause(5.0)
    hide c1 with w21
    show c2 at truecenter with w21
    $ renpy.pause(5.0)
    hide c2 with w21
    show c3 at truecenter with w21
    $ renpy.pause(3.0)
    hide c3 with w21
    show c4 at truecenter with w21
    $ renpy.pause(3.0)
    hide c4 with w21
    show c5 at truecenter with w21
    $ renpy.pause(3.0)
    hide c5 with w21
    show c6 at truecenter with w21
    $ renpy.pause(3.0)
    hide c6 with w21
    show c7 at truecenter with w21
    $ renpy.pause(3.0)
    hide c7 with w21
    show c8 at truecenter with w21
    $ renpy.pause(3.0)
    hide c8 with w21
    show c9 at truecenter with w21
    $ renpy.pause(3.0)
    hide c9 with w21
    show c10 at truecenter with w21
    $ renpy.pause(3.0)
    hide c10 with w21
    show c11 at truecenter with w21
    $ renpy.pause(3.0)
    hide c11 with w21
    scene endscreen with w20
    $ renpy.pause(0.25)
    show endscreen2 with w9
    $ renpy.pause(10.0)
    hide endscreen2 with w9
    scene endscreen3 with w20
    $ renpy.pause()
    stop music fadeout 2.0
    scene black with w12
    $ renpy.pause(1.0)
    return
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
