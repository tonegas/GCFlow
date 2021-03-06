import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from space import Ball
from layers import GenericLayer
from utils import to_one_hot_vect

time_end = 100000
time_step = 0.01

# l = LinearLayer(2,5)
# s = SoftMaxLayer()
# n = Sequential(l,s)
#
# x = np.array([1,2])
# t = np.array([0,-0.5,0,0,0])
#
# y = n.forward(x)
# print y
#
# loss = NegativeLogLikelihoodLoss()
#
# J = loss.loss(y,t)
# dJdy = loss.dJdy_gradient(y,t)
# dJdx_softmax = s.backward(dJdy)
#
# print dJdx_softmax
# dJdx = l.backward(dJdx_softmax)
# print dJdx
# l.W -= l.dJdW_gradient(dJdx_softmax)
# print n.forward(np.array([1,2]))

from network import Sequential
from layers import SoftMaxLayer, LinearLayer, TanhLayer, NormalizationLayer, RandomGaussianLayer
from qlearning import GenericAgent
from losses import NegativeLogLikelihoodLoss
from trainer import Trainer
from optimizers import GradientDescentMomentum, GradientDescent, AdaGrad

interval = 0
load = 1

if load == 1:
    agent = GenericLayer.load('genericagent.net')
    # from printers import Printer2D
    # p = Printer2D()
    # p.print_model(2,agent.net,np.array([[0,0],[5.0,5.0]]),[4,5])
    # plt.show()
else:
    # norm = NormalizationLayer(
    #     np.array([0.0,0.0,-10.0,-10.0]),
    #     np.array([5.0,5.0,10.0,10.0]),
    #     np.array([-1.0,-1.0,-1.0,-1.0]),
    #     np.array([1.0,1.0,1.0,1.0])
    # )
    norm = NormalizationLayer(
        np.array([0.0,0.0]),
        np.array([5.0,5.0]),
        np.array([-1.0,-1.0]),
        np.array([1.0,1.0])
    )

    n = Sequential(
        norm,
        # LinearLayer(2,5,weights='gaussian'),
        # TanhLayer,
        #AddGaussian(1),
        LinearLayer(2,4,weights='gaussian'),
        RandomGaussianLayer(1),
        SoftMaxLayer
    )
    agent = GenericAgent(n,4,40,5.0)
    agent.set_training_options(
        Trainer(),
        NegativeLogLikelihoodLoss(),
        GradientDescentMomentum(learning_rate=0.1, momentum=0.7) #GradientDescent(learning_rate=0.2)
    )

start = np.array([3.5,3.5])
obstacles = [
    # np.array([2.5,2.5,1.0])
]
win = np.array([0.5,0.5,0.5])


def data_gen(t=0):
    ball = Ball(np.random.rand(1,2)[0]*5)
    time_start_game = 0
    for ind,time in enumerate(np.linspace(0,time_end,time_end/time_step)):
        state = np.array([ball.p[0],ball.p[1]])

        if time - time_start_game >=5.0:
            agent.reinforcement(state,-0.3)
            ball = Ball(start)
            agent.clear()
            time_start_game = time

         #print state
        if ball.lose == 0:
            if ball.win:
                agent.reinforcement(state,0.3)
                ball = Ball(np.random.rand(1,2)[0]*5)
                agent.clear()
                time_start_game = time

            # agent.reinforcement(state,0.001)
            ind_command = np.argmax(agent.reinforcement(state,0))
            #print ind_command
            command = 0
            if ind_command == 0:
                command = np.array([4,0])
            elif ind_command == 1:
                command = np.array([-4,0])
            elif ind_command == 2:
                command = np.array([0,4])
            elif ind_command == 3:
                command = np.array([0,-4])

            ball.step(time_step, command, obstacles, win)
        else:
            # print 'boing'
            agent.reinforcement(state,-0.3)
            ball = Ball(np.random.rand(1,2)[0]*5)
            time_start_game = time
            agent.clear()

        if int(ind%1000) == 0:
            # print (agent.net.elements[0].W[0][3],agent.net.elements[0].W[1][3],agent.net.elements[0].W[2][3])
            # print agent.net.elements[1].W
            print np.max(agent.model.elements[1].W)
            agent.save('genericagent.net')
        yield (ball,)

fig = plt.figure(1)
ax = plt.subplot(111)

ax.grid()
ballPoint, = ax.plot(0, 0, color='r', marker='o', linestyle='none')
obstablesCircles = []
for i,ob in enumerate(obstacles):
    obstablesCircles = plt.Circle((ob[0], ob[1]), ob[2], color='r')
    ax.add_artist(obstablesCircles)

winCircle = plt.Circle((win[0], win[1]), win[2], color='g')
ax.add_artist(winCircle)
ax.set_xlim(0,5)
ax.set_ylim(0,5)

def run(data):
    # pass
    ballPoint.set_xdata(data[0].p[0])
    ballPoint.set_ydata(data[0].p[1])

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=interval, repeat=False)
plt.show()
