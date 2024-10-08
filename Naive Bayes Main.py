from typing import List, Dict, Union
import os
import math
from utils.sentiment_detection import read_tokens, load_reviews, split_data
from exercises.tick1 import accuracy, predict_sentiment, read_lexicon


def calculate_class_log_probabilities(training_data: List[Dict[str, Union[List[str], int]]]) \
        -> Dict[int, float]:
    """
    Calculate the prior class probability P(c).

    @param training_data: list of training instances, where each instance is a dictionary with two fields: 'text' and
        'sentiment'. 'text' is the tokenized review and 'sentiment' is +1 or -1, for positive and negative sentiments.
    @return: dictionary from sentiment to prior log probability
    """
    sentiment_counts = {1: 0, -1: 0}
    total_instances = len(training_data)
    for instance in training_data:
        sentiment = instance['sentiment']
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1
    prior_log_probabilities = {}
    for sentiment, count in sentiment_counts.items():
        prior_probability = count / total_instances
        prior_log_probabilities[sentiment] = math.log(prior_probability)
    return prior_log_probabilities


def calculate_unsmoothed_log_probabilities(training_data: List[Dict[str, Union[List[str], int]]]) \
        -> Dict[int, Dict[str, float]]:
    """
    Calculate the unsmoothed log likelihood log (P(x|c)) of a word in the vocabulary given a sentiment.

    @param training_data: list of training instances, where each instance is a dictionary with two fields: 'text' and
        'sentiment'. 'text' is the tokenized review and 'sentiment' is +1 or -1, for positive and negative sentiments.
    @return: dictionary from sentiment to Dictionary of tokens with respective log probability
    """
    all_word = list()
    for instance in training_data:
        all_word += instance['text']
    all_word = set(all_word)
    word_sentiment_count = {w: {1: 0, -1: 0} for w in all_word}
    sentiment_count = {1: 0, -1: 0}
    for instance in training_data:
        word_ls = instance['text']
        sentiment = instance['sentiment']
        for w in word_ls:
            word_sentiment_count[w][sentiment] += 1
            sentiment_count[sentiment] += 1
    prior_log_prob = {1: {}, -1: {}}
    for word, dct in word_sentiment_count.items():
        for sent, num in dct.items():
            if num > 0:
                prior_log_prob[sent][word] = math.log(num / (sentiment_count[sent]))
            else:
                prior_log_prob[sent][word] = -1e100
    return prior_log_prob


def calculate_smoothed_log_probabilities(training_data: List[Dict[str, Union[List[str], int]]]) \
        -> Dict[int, Dict[str, float]]:
    """
    Calculate the smoothed log likelihood log (P(x|c)) of a word in the vocabulary given a sentiment. Use the smoothing
    technique described in the instructions (Laplace smoothing).

    @param training_data: list of training instances, where each instance is a dictionary with two fields: 'text' and
        'sentiment'. 'text' is the tokenized review and 'sentiment' is +1 or -1, for positive and negative sentiments.
    @return: Dictionary from sentiment to Dictionary of tokens with respective log probability
    """
    all_word = list()
    for instance in training_data:
        all_word += instance['text']
    all_word = set(all_word)
    word_sentiment_count = {w: {1: 0, -1: 0} for w in all_word}
    sentiment_count = {1: 0, -1: 0}
    for instance in training_data:
        word_ls = instance['text']
        sentiment = instance['sentiment']
        for w in word_ls:
            word_sentiment_count[w][sentiment] += 1
            sentiment_count[sentiment] += 1
    prior_log_prob = {1: {}, -1: {}}
    for word, dct in word_sentiment_count.items():
        for sent, num in dct.items():
            if num > 0:
                prior_log_prob[sent][word] = math.log((num + 1) / (sentiment_count[sent] + len(all_word)))
            else:
                prior_log_prob[sent][word] = -1e100
    return prior_log_prob


def predict_sentiment_nbc(review: List[str], log_probabilities: Dict[int, Dict[str, float]],
                          class_log_probabilities: Dict[int, float]) -> int:
    """
    Use the estimated log probabilities to predict the sentiment of a given review.

    @param review: a single review as a list of tokens
    @param log_probabilities: dictionary from sentiment to Dictionary of tokens with respective log probability
    @param class_log_probabilities: dictionary from sentiment to prior log probability
    @return: predicted sentiment [-1, 1] for the given review
    """
    total_score = dict(class_log_probabilities)
    for word in review:
        total_score[-1] += log_probabilities[-1].get(word, 0)
        total_score[1] += log_probabilities[1].get(word, 0)

    predicted_sentiment = max(total_score, key=total_score.get)

    return predicted_sentiment


def main():
    """
    Code to check your work locally (run this from the root directory, 'mlrd/')
    """
    review_data = load_reviews(os.path.join('data', 'sentiment_detection', 'reviews'))
    training_data, validation_data = split_data(review_data, seed=0)
    train_tokenized_data = [{'text': read_tokens(x['filename']), 'sentiment': x['sentiment']} for x in training_data]
    dev_tokenized_data = [read_tokens(x['filename']) for x in validation_data]
    validation_sentiments = [x['sentiment'] for x in validation_data]

    lexicon = read_lexicon(os.path.join('data', 'sentiment_detection', 'sentiment_lexicon'))

    preds_simple = []
    for review in dev_tokenized_data:
        pred = predict_sentiment(review, lexicon)
        preds_simple.append(pred)

    acc_simple = accuracy(preds_simple, validation_sentiments)
    print(f"Your accuracy using simple classifier: {acc_simple}")

    class_priors = calculate_class_log_probabilities(train_tokenized_data)
    unsmoothed_log_probabilities = calculate_unsmoothed_log_probabilities(train_tokenized_data)
    preds_unsmoothed = []
    for review in dev_tokenized_data:
        pred = predict_sentiment_nbc(review, unsmoothed_log_probabilities, class_priors)
        preds_unsmoothed.append(pred)

    acc_unsmoothed = accuracy(preds_unsmoothed, validation_sentiments)
    print(f"Your accuracy using unsmoothed probabilities: {acc_unsmoothed}")

    smoothed_log_probabilities = calculate_smoothed_log_probabilities(train_tokenized_data)
    preds_smoothed = []
    for review in dev_tokenized_data:
        pred = predict_sentiment_nbc(review, smoothed_log_probabilities, class_priors)
        preds_smoothed.append(pred)

    acc_smoothed = accuracy(preds_smoothed, validation_sentiments)
    print(f"Your accuracy using smoothed probabilities: {acc_smoothed}")


if __name__ == '__main__':
    main()
