from typing import List, Dict
import os
import sys


# access the parent directory of the code
# parent_path = os.path.join(os.path.pardir, os.path.abspath(os.path.dirname(__file__)))
# sys.path.append(parent_path)

from utils.sentiment_detection import read_tokens, load_reviews


def read_lexicon(filename: str) -> Dict[str, int]:
    """
    Read the lexicon from a given path.

    @param filename: path to file
    @return: dictionary from word to sentiment (+1 or -1 for positive or negative sentiments respectively).
    """

    lexicon = {}
    with open("/Users/pratyushsinghal/Desktop/IB /CCIR/mlrd1/data/sentiment_detection/sentiment_lexicon", encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            line_ls = line.split(' ')
            word = line_ls[0].split('=')[1]
            sentiment = line_ls[2].split('=')[1]
            if sentiment == 'negative':
                lexicon[word] = -1
            elif sentiment == 'positive':
                lexicon[word] = 1
            else:
                print(sentiment)
                raise ValueError('illegal sentiment!')
    return lexicon


def predict_sentiment(review: List[str], lexicon: Dict[str, int]) -> int:
    """
    Given a list of tokens from a tokenized review and a lexicon, determine whether the sentiment of each review in the
    test set is positive or negative based on whether there are more positive or negative words.

    @param review: list of tokens from tokenized review
    @param lexicon: dictionary from word to sentiment (+1 or -1 for positive or negative sentiments respectively).
    @return: calculated sentiment for each review (+1 or -1 for positive or negative sentiments respectively).
    """
    pos_count = 0
    neg_count = 0

    for word in review:
        if word in lexicon:
            sentiment = lexicon[word]
            if sentiment == 1:
                pos_count += 1
            elif sentiment == -1:
                neg_count += 1

    if pos_count > neg_count:
        return 1
    elif pos_count < neg_count:
        return -1
    else:
        return 0


def accuracy(pred: List[int], true: List[int]) -> float:
    """
    Calculate the proportion of predicted sentiments that were correct.

    @param pred: list of calculated sentiment for each review
    @param true: list of correct sentiment for each review
    @return: the overall accuracy of the predictions
    """
    correct = 0
    for counter in range(len(pred)):
        if pred[counter] == true[counter]:
            correct += 1

    return correct / len(pred)


def predict_sentiment_improved(review: List[str], lexicon: Dict[str, int]) -> int:
    """
    Use the training data to improve your classifier, perhaps by choosing an offset for the classifier cutoff which
    works better than 0.

    @param review: list of tokens from tokenized review
    @param lexicon: dictionary from word to sentiment (+1 or -1 for positive or negative sentiments respectively).
    @return: calculated sentiment for each review (+1, -1 for positive and negative sentiments, respectively).
    """
    pos_count = 0
    neg_count = 0

    for word in review:
        if word in lexicon:
            sentiment = lexicon[word]
            if (sentiment == 1):
                pos_count += 1
            elif (sentiment == -1):
                neg_count += 1

    threshold = 7
    value = pos_count - neg_count
    if value > threshold:
        return 1
    else:
        return -1


def main():
    """
    Code to check your work locally (run this from the root directory, 'mlrd/')
    """
    review_data = load_reviews("/Users/pratyushsinghal/Desktop/IB /CCIR/mlrd1/data/sentiment_detection/reviews/")
    tokenized_data = [read_tokens(x['filename']) for x in review_data]

    lexicon = read_lexicon("/Users/pratyushsinghal/Desktop/IB /CCIR/mlrd1/data/sentiment_detection/sentiment_lexicon")

    pred1 = [predict_sentiment(t, lexicon) for t in tokenized_data]
    acc1 = accuracy(pred1, [x['sentiment'] for x in review_data])
    print(f"Your accuracy: {acc1}")

    pred2 = [predict_sentiment_improved(t, lexicon) for t in tokenized_data]
    acc2 = accuracy(pred2, [x['sentiment'] for x in review_data])
    print(f"Your improved accuracy: {acc2}")


if __name__ == '__main__':
    main()
