import tensorflow as tf
import numpy as np
import SA.NeuralNet.my_txtutils as my_txtutils

#Runs A Trained NEURAL NETWORK and writes output to a text file.


def nnout():
    ALPHASIZE = my_txtutils.ALPHASIZE
    NLAYERS = 3
    INTERNALSIZE = 512
    #CHANGE THIS VALUE TO CHANGE MODEL VVVVVVVVVV
    TrainedModel = "checkpoints/rnn_train_1546846462-30000000"
    MetaGraph = TrainedModel +".meta"

    author = TrainedModel

    ncnt = 0
    with tf.Session() as sess:
        new_saver = tf.train.import_meta_graph(MetaGraph)
        new_saver.restore(sess, author)
        x = my_txtutils.convert_from_alphabet(ord("L"))
        x = np.array([[x]])  # shape [BATCHSIZE, SEQLEN] with BATCHSIZE=1 and SEQLEN=1

        # initial values
        y = x
        h = np.zeros([1, INTERNALSIZE * NLAYERS], dtype=np.float32)  # [ BATCHSIZE, INTERNALSIZE * NLAYERS]
        file = open("generated_output.txt", "w")
        for i in range(10000):
            yo, h = sess.run(['Yo:0', 'H:0'], feed_dict={'X:0': y, 'pkeep:0': 1., 'Hin:0': h, 'batchsize:0': 1})

            # If sampling is be done from the topn most likely characters, the generated text
            # is more credible and more "english". If topn is not set, it defaults to the full
            # distribution (ALPHASIZE)

            # Recommended: topn = 10 for intermediate checkpoints, topn=2 or 3 for fully trained checkpoints

            c = my_txtutils.sample_from_probabilities(yo, topn=2)
            y = np.array([[c]])  # shape [BATCHSIZE, SEQLEN] with BATCHSIZE=1 and SEQLEN=1
            c = chr(my_txtutils.convert_to_alphabet(c))
            print(c, end="")
            file.write(c)

            if c == '\n':
                ncnt = 0
            else:
                ncnt += 1
            if ncnt == 100:
                print("")
                file.write("")
                ncnt = 0
        file.close()
