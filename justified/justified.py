"""
Knuth-Plass Text Justification (Dynamic Programming)
Benjamin Yates, 2016

Inspired by  my favorite  of the MIT OpenCourseWare lectures
for 6.006 Introduction to Algorithms:

https://www.youtube.com/watch?v=ENyox7kNKeY

The last  line of  the  paragraph  remains  unjustified.  To
do  this,  the last line does not contribute  to  the  total
badness,  and the  output pass does not  expand it.  I'm not
sure how it is implemented in LaTeX, but this  method  seems
to work well. 

Because this is a fixed-width justification routine, it  may
distribute  uneven amounts of  padding as  it expands lines.
A  PRNG seeded  with the  line-text itself  is  used to give
stable, uniform distribution of the padding spaces.

This docstring was formatted by this code.
"""
from random import Random

DEMO_WIDTH = 60

MOBY = """
No, when I go to sea, I go as a simple sailor, right before the mast,
plumb down into the forecastle, aloft there to the royal mast-head. True,
they rather order me about some, and make me jump from spar to spar, like
a grasshopper in a May meadow. And at first, this sort of thing is
unpleasant enough. It touches one's sense of honour, particularly if you
come of an old established family in the land, the Van Rensselaers, or
Randolphs, or Hardicanutes. And more than all, if just previous to putting
your hand into the tar-pot, you have been lording it as a country
schoolmaster, making the tallest boys stand in awe of you. The transition
is a keen one, I assure you, from a schoolmaster to a sailor, and requires
a strong decoction of Seneca and the Stoics to enable you to grin and bear
it. But even this wears off in time.
""".strip()


def main():
    print KnuthPlassFormatter(DEMO_WIDTH).format(MOBY)


class KnuthPlassFormatter(object):
    def __init__(self, width):
        self.width = width

    def format(self, text):
        """
        Format a paragraph string as fully justified text

        Args:
            text: one parapgraph of text to format

        Returns:
            formatted text string
        """
        self._memo = {}
        self._parent = {}
        self.words = text.split()
        self.best_break(0, len(self.words))
        return '\n'.join(self.wrapped_lines())

    def packed(self, words):
        """Fit set of words as tightly as possible."""
        return ' '.join(words)

    def expanded(self, words, width):
        """Fit set of words in <width> chars, padding as needed"""
        if len(words) == 1:
            return words[0]

        unspaced_words = ''.join(words)

        length = len(unspaced_words)
        space_left = width - length
        gaps = [0 for _ in range(len(words) - 1)]
        while space_left:
            for idx, gap in enumerate(gaps):
                if not space_left:
                    break
                gaps[idx] += 1
                space_left -= 1

        # stable, random distribution of spaces
        Random(unspaced_words).shuffle(gaps)
        gaps.append(0)  # one empty gap for zip()

        spaces = (gap * ' ' for gap in gaps)
        return ''.join(word + space for word, space in zip(words, spaces))

    def badness(self, i, j):
        """LaTeX 'badness' function"""
        # fun: try adding a non-negative value to length
        length = len(self.packed(self.words[i:j]))  # + 20
        if length > self.width:
            return float('inf')
        else:
            return (self.width - length) ** 3.0
        
    def best_break(self, i, j):
        """
        dynamic program for finding the best locations to place
        line-breaks in a paragraph when producing fully justified
        text

        Args:
            i: start word index, inclusive
            j: last word index, inclusive

        Returns:
            best (minimum) badness score found

        Side-effect:
            _memo & _parent are updated with scores and links
            for finding the final path through the graph after
            all line-breaks are found.
        """
        try:
            return self._memo[(i, j)]
        except KeyError:
            pass

        if j == len(self.words):
            length = len(self.packed(self.words[i:j]))
            if length <= self.width:
                # base-case: this is the last line.
                # it doesn't contribute badness
                self._memo[(i, j)] = 0
                self._parent[i] = j
                return 0

        # evaluate every possible break position
        vals = []
        for n in reversed(range(i, j)):
            total_badness = self.badness(i, n + 1) + self.best_break(n + 1, j)
            vals.append((total_badness, n + 1))

        # choose the break with the minimum total badness
        best_val, best_idx = min(vals, key=lambda pair: pair[0])
        self._memo[(i, j)] = best_val
        self._parent[i] = best_idx
        return best_val

    def wrapped_lines(self):
        """
        render a paragraph of justified text using the graph
        constructed by best_break()

        Returns:
            paragraph (string) of justified text
        """
        a = 0
        b = self._parent[0]
        while True:
            words = self.words[a:b]

            if b == len(self.words):
                # this is the last line, so
                # we don't justify the text
                yield self.packed(words)
                return

            yield self.expanded(words, self.width)
            a = b
            b = self._parent[a]


class GreedyFormatter(KnuthPlassFormatter):

    def format(self, text):
        """
        Format a paragraph string as fully justified text
        using a greedy method

        Args:
            text: one parapgraph of text to format

        Returns:
            formatted text string
        """
        self._memo = {}
        self._parent = {}
        self.words = text.split()
        self.lines = []
        cur_line = []
        for word in self.words:
            tmp = cur_line + [word]
            if len(self.packed(tmp)) <= self.width:
                cur_line += [word]
            else:
                self.lines.append(cur_line)
                cur_line = [word]
        if cur_line:
            self.lines.append(cur_line)
        return '\n'.join(self.wrapped_lines())

    def wrapped_lines(self):
        last = len(self.lines) - 1
        for idx, words in enumerate(self.lines):
            if idx == last:
                yield self.packed(words)
                return
            yield self.expanded(words, self.width)


TextFormatter = KnuthPlassFormatter


if __name__ == '__main__':
    main()

# vim: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
