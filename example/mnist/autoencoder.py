from mnist_load import load_mnist_dataset
import numpy as np
import matplotlib.pyplot as plt
from layers import NormalizationLayer, LinearLayer, TanhLayer, ReluLayer, SigmoidLayer
from network import Sequential
from genericlayer import StoreNetwork
from trainer import Trainer
from losses import NegativeLogLikelihoodLoss, CrossEntropyLoss, SquaredLoss
from optimizers import GradientDescent, GradientDescentMomentum, AdaGrad
from printers import ShowTraining
from utils import SharedWeights, to_one_hot_vect

from standart_network.autoencoder import AutoEncoder


num_classes = 10
name_net = "mnist.net"
load_net = False
epochs = 500


train = load_mnist_dataset(dataset = "training", path = "./mnist")
test = load_mnist_dataset(dataset = "testing", path = "./mnist")

W = SharedWeights('gaussian', 784, 32)

if load_net:
    print "Load Network"
    model = StoreNetwork.load(name_net)
else:
    print "New Network"
    #Two layer network
    ae = AutoEncoder(784, [
        {"size" : 32, "output_layer" :TanhLayer, "weights" : W},
        {"size" : 784, "output_layer" :TanhLayer}#, "weights": W.T()}
    ])
    ae.choose_network([0,1])
    #ae.choose_network()
    model = Sequential([
        NormalizationLayer(0,255,-0.1,0.1),
        ae,
        NormalizationLayer(-1,1,0,255),
    ])

plt.figure(12)
plt.figure(13)

train = [(t/255.0,t/255.0) for (t,v) in train[:100]]
# train = [(t,t) for (t,v) in train[:100]]

display = ShowTraining(epochs_num = epochs)

trainer = Trainer(show_training = True, show_function = display.show)

J_list, dJdy_list = trainer.learn(
    model = ae,
    train = train,
    # loss = NegativeLogLikelihoodLoss(),
    # loss = CrossEntropyLoss(),
    loss = SquaredLoss(),
    # optimizer = GradientDescent(learning_rate=0.3),
    # optimizer = GradientDescentMomentum(learning_rate=0.01, momentum=0.5),
    optimizer = GradientDescentMomentum(learning_rate=0.005/10, momentum=0.7),
    # optimizer= AdaGrad(learning_rate=0.01),
    epochs = epochs,
    batch_size = 10
)

for ind, (t,v) in enumerate(train[:10]):
    plt.figure(12)
    plt.subplot(2,len(train[:10]),ind+1)
    plt.imshow(v.reshape(28,28), cmap=plt.get_cmap('Greys'))
    plt.subplot(2,len(train[:10]),ind+11)
    plt.imshow(ae.forward(t).reshape(28,28), cmap=plt.get_cmap('Greys'))
    # plt.imshow(model.forward(t).reshape(28,28), cmap=plt.get_cmap('Greys'))


for ind in range(25):
    plt.figure(13)
    plt.subplot(5,5,ind+1)
    plt.imshow(W.get()[ind,:].reshape(28,28), cmap=plt.get_cmap('Greys'))

plt.show()

raw_input('Press ENTER to exit')

model.save('model.net')