from os import path, getcwd

import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector

from common import WORD_METADATA_FILENAME, SENTENCE_METADATA_FILENAME, WORDS_FEATURE, \
    tic, toc, create_parser_training, parse_arguments, \
    preprocess_data, run_experiment, estimator_spec_for_softmax_classification

# Default values
MODEL_DIRECTORY = 'perceptron_model'
NUM_EPOCHS = 2
BATCH_SIZE = 64
LEARNING_RATE = 0.05


def bag_of_words_perceptron_model(features, labels, mode, params):
    """Perceptron architecture"""
    with tf.variable_scope('Perceptron'):
        bow_column = tf.feature_column.categorical_column_with_identity(
            WORDS_FEATURE, num_buckets=params.n_words)
        # By default embeding_column combines the word embedding values by taking the mean value
        # of the embedding values over the document words. Try weighted sum, via sqrtn?
        bow_embedding_column = tf.feature_column.embedding_column(
            bow_column, dimension=params.output_dim)
        logits = tf.feature_column.input_layer(
            features,
            feature_columns=[bow_embedding_column])

    return estimator_spec_for_softmax_classification(logits, labels, mode, params)


def perceptron():
    """Train and evaluate the perceptron model."""
    tf.logging.set_verbosity(FLAGS.verbosity)

    print("Preprocessing data...")
    tic()
    train_raw, x_train, y_train, x_test, y_test, classes = preprocess_data(FLAGS)
    toc()

    # Set the output dimension according to the number of classes
    FLAGS.output_dim = len(classes)

    # Train and evaluate the model.
    tic()
    run_experiment(x_train, y_train, x_test, y_test, bag_of_words_perceptron_model, 'train_and_evaluate', FLAGS)
    toc()


# Run script ##############################################
if __name__ == "__main__":
    parser = create_parser_training(MODEL_DIRECTORY, NUM_EPOCHS, BATCH_SIZE, LEARNING_RATE)
    parser.add_argument(
        '--word-meta-file',
        default=WORD_METADATA_FILENAME,
        help='Word embedding metadata filename (default: {})'.format(WORD_METADATA_FILENAME))
    parser.add_argument(
        '--sent-meta-file',
        default=SENTENCE_METADATA_FILENAME,
        help='Sentence embedding metadata filename (default: {})'.format(SENTENCE_METADATA_FILENAME))

    FLAGS = parse_arguments(parser)

    perceptron()
