from cmu_graphics import *
import random
from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
import os
# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("./converted_keras/keras_model.h5", compile=False)

# Load the labels
class_names = open("./converted_keras/labels.txt", "r").readlines()

# CAMERA can be 0 or 1 based on default camera of your computer
camera = cv2.VideoCapture(0)


#Instructions#
#Hold your right hand at a close distance to the camera. Make sure it is clearly visible. Make a fist to not jump. Open your hand to jump. Collect cans for energy.

#collect audio
#public domain, audio from OpenGameArt, creator:Fupi
#collectsoundpath = r"./Media/coin-shortened.mp3"
#collect_sound = Sound(collectsoundpath)


#losing audio
#game_over=Sound("./Media/404743__owlstorm__retro-video-game-sfx-fail.wav")


#jump audio
#bounce_sound_path = r"./Media/coin-shortened.mp3"
#bounce=Sound(bounce_sound_path)

#background
skyURL = "https://img.freepik.com/premium-vector/cloud-sky-with-pixel-art-style_475147-110.jpg"
sky=Image(skyURL, 0, 0, width=400, height=400)

#redbull spawn variables
CanSpawnInterval = 15
#speed
person_speed=6
redbull_speed=5


#some variables
freefall = 0
stillPlaying = True
stepCount=0
app.stepsPerSecond = 30
is_jumping = False



#redbull model
#credit: ThePixelPocket
redbullURL = "https://art.pixilart.com/0a98b51febc7acd.png"
###################
newCan = Image(redbullURL,random.randint(0,400),0, width=40, height=40)


cangroup=Group(
    newCan
    )
###################
#making the person
#credit for art:MaikeruThePlayer on Deviantart
personURL = "./Media/megaman.png" #I changed the model because the previous one was acting weird.
person=Image(personURL,0,0, width=60, height=60)

#keeping track of the score
score = Label(0,350,30,size=20,bold=True)



#making the energy bar
energy=100

energy_string=Label("Energy Level: ",80,30,size=20, fill='white')
energy_score=Label(0,155,30,size=20, fill='white')

endOfGameMessage = Label('YOU LOSE', 200, 200, fill='white', size=50, bold=True)
endOfGame = Group(
    Rect(200, 200, 300, 70, fill='blue', align='center'),
    endOfGameMessage
    )
endOfGame.visible = False

###################
#Spawning cans function
def CanSpawn():
    global newCan
    newCan = Image(redbullURL,random.randint(0,400),0, width=40, height=40)
    cangroup.add(newCan)


###################



def TriggeredJump():
    # Grab the webcamera's image.
    ret, image = camera.read()

    # Resize the raw image into (224-height,224-width) pixels
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

    # Show the image in a window
    cv2.imshow("Webcam Image", image)

    # Make the image a numpy array and reshape it to the models input shape.
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

    # Normalize the image array
    image = (image / 127.5) - 1

    # Predicts the model
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    decision = class_name[2:] #decision between the two options the model was trained on
    jump_triggered = (decision.strip()=="Jump")  #the jump is triggered if the camera detects and decides on the lable "Jump"
    


    os.system("cls") #clears the terminal so it looks nice
    print("Class:", class_name[2:], end="")
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
    print(jump_triggered)
    print(decision.strip()=="Jump")
    print(decision)
    
    #printing these for troubleshooting and making sure everything is ok

    return jump_triggered



###################
def jump():
    
    global freefall
    global energy
    if energy>1:
        freefall=0 #falling speed does not have an effect on jumping height
        freefall-=4
        energy-=30
        #bounce.play()



#Animations
def onStep():
    global person_speed, freefall, stillPlaying, stepCount, energy, redbull_speed, newCan, is_jumping
    
    stepCount+=1
    
    jump_triggered = TriggeredJump() #jump triggered means the model has decided it is seeing an open hand, meaning the character is ready to jump.
    should_jump = (jump_triggered and (is_jumping==False)) #we should jump if we are not currently jumping AND the camera is seeing an open hand. The next few lines make it so that I am not constantly going up whem my hand is opened. 
    print(should_jump)

    if jump_triggered:
        if should_jump:
            is_jumping = True
            print("jumping")
            jump()
    else:
        is_jumping = False
    #when we jump is_jumping is set to true because should_jump is only true if is_jumping is false. This makes it so that you don't constantly go up when your hand is opened.



    
    #if stillPlaying == False:
        #camera.release()
        #cv2.destroyAllWindows()


    #updating the energy score
    if stillPlaying:
        energy_score.value=energy

    #spawning cans
    if stepCount%CanSpawnInterval==0:
        CanSpawn()
    



    #it's raining redbull
    cangroup.bottom += redbull_speed




    #making the person go from left to right

    person.left+=person_speed
    if person.right>=400:
        person_speed*=-1
        

    if person.left<=0:
        person_speed*=-1


    #making the person fall
    person.top+=freefall
    freefall+=0.3


    #removing the shape that is hit and collecting energy
    if energy<100:
        for c in cangroup.children:

            if person.hitsShape(c):
                cangroup.remove(c)
                energy+=20
                #collect_sound.play()
    

    #capping energy
    if energy>100:
        energy=100
    if energy<0:
        energy=0



    #updating score
    if stillPlaying:
        score.value=stepCount




    #losing the game
    if person.top>=400:
        endOfGame.visible = True
        stillPlaying=False
        #game_over.play()
        stepCount=0 #stops adding to the score
        app.stepsPerSecond = 0 #stops running
        
    if person.bottom<=0:
        endOfGame.visible = True
        stillPlaying=False
        #game_over.play()
        stepCount=0 #stops adding to the score
        app.stepsPerSecond = 0 #stops running
    





#bouncing the person
def onKeyPress(space):
        global freefall
        global energy
        if energy>1:
            freefall=0 #falling speed does not have an effect on jumping height
            freefall-=4
            energy-=30
            #bounce.play()




    












cmu_graphics.run()