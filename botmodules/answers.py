import random

def the_answer(self, e):
    answers = """If you think your bike looks good, it does.
If you like the way your bike rides, it's an awesome bike.
You don't need to spend a million dollars to have a great bike, but if you do spend a million dollars and know what you want you'll probably also have a great bike.
Yes, you can tour on your bike – whatever it is.
Yes, you can race on your bike – whatever it is.
Yes, you can commute on your bike – whatever it is.
26” wheels or 29” or 650b or 700c or 24” or 20” or whatever – yes, that wheel size is rad and you'll probably get where you're going.
Disc brakes, cantis, v-brakes, and road calipers all do a great job of stopping a bike when they're working and adjusted.
No paint job makes everyone happy.
Yes, you can put a rack on that. Get some p-clamps if there are no mounts.
Steel is a great material for making bike frames - so is aluminum, carbon fiber, and titanium.
You can have your saddle at whatever angle makes you happy.
Your handlebars can be lower than your saddle, even with your saddle, or higher than your saddle. Whichever way you like it is right.
Being shuttled up a downhill run does not make you a weak person, nor does choosing not to fly off of a 10 foot drop.
Bike frames made overseas can be super cool. Bike frames made in the USA can be super cool.
Hey, tattooed and pierced long shorts wearin' flat brim hat red bull drinkin white Oakley sportin rad person on your full suspension big hit bike – nice work out there.
Hey, little round glasses pocket protector collared shirt skid lid rear view mirror sandal wearing schwalbe marathon running pletscher two-leg kickstand tourist – good job.
Hey, shaved leg skinny as hell super duper tan line hear rate monitor checking power tap train in the basement all winter super loud lycra kit million dollar wheels racer – keep it up.
The more you ride your bike, the less your ass will hurt.
The following short answers are good answers, but not the only ones for the question asked – 29”, Brooks, lugged, disc brake, steel, Campagnolo, helmet, custom, Rohloff, NJS, carbon, 31.8, clipless, porteur.
No bike does everything perfectly. In fact, no bike does anything until someone gets on it to ride.
Sometimes, recumbent bikes are ok.
Your bike shop is not trying to screw you. They're trying to stay open.
Buying things off of the internet is great, except when it sucks.
Some people know more about bikes than you do. Other people know less.
Maybe the person you waved at while you were out riding didn't see you wave at them.
It sucks to be harassed by assholes in cars while you're on a bike. It also sucks to drive behind assholes on bikes.
Did you build that yourself? Awesome. Did you buy that? Cool.
Wheelies are the best trick ever invented. That's just a fact.
Which is better, riding long miles, or hanging out under a bridge doing tricks? Yes.
Yes, you can break your collar bone riding a bike like that.
Stopping at stop signs is probably a good idea.
Driving with your bikes on top of your car to get to a dirt trail isn't ideal, but for most people it's necessary.
If your bike has couplers, or if you have a spendy bike case, or if you pay a shop to pack your bike, or if you have a folding bike, shipping a bike is still a pain in the ass for everyone involved.
That dent in your frame is probably ok, but maybe it's not. You should get it looked at.
Touch up paint always looks like shit. Often it looks worse than the scratch.
A pristine bike free of dirt, scratches, and wear marks makes me sort of sad.
A bike that's been chained to the same tree for three years caked with rust and missing parts makes me sad too.
Bikes purchased at Wal-mart, Target, Costco, or K-mart are generally not the best bang for your buck.
Toe overlap is not the end of the world, unless you crash and die – then it is.
Sometimes parts break. Sometimes you crash. Sometimes it's your fault.
Yes, you can buy a bike without riding it first. It would be nice to ride it first, but it's not a deal breaker not to.
Ownership of a truing stand does not a wheel builder make.
32 spokes, 48 spokes, 24 spokes, three spokes? Sure.
Single speed bikes are rad. Bikes with derailleurs and cassettes are sexy. Belt drive internal gear bikes work great too.
Columbus, TruTemper, Reynolds, Ishiwata, or no brand? I'd ride it.
Tubeless tires are pretty cool. So are tubes.
The moral of RAGBRAI is that families and drunken boobs can have fun on the same route, just maybe at different times of day.
Riding by yourself kicks ass. You might also try riding with a group.
Really fast people are frustrating, but they make you faster. When you get faster, you might frustrate someone else.
Stopping can be as much fun as riding.
Lots of people worked their asses off to build whatever trail or road or alley you're riding on. You should thank them."""

    answer_list = answers.split("\n")

    e.output = answer_list[int(random.random()*len(answer_list)+1)]
    return e
    
the_answer.command="!answer"
