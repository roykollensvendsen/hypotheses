Random:
Hey guys, am I in the right place for a new idea or is there a better channel?

I've been thinking about something: what if connectivity is the foundation and separation is the emergence?

Most AI starts from isolated nodes and builds connections. I want to test the opposite. All nodes start maximally connected, training happens through selective disconnection. Pruning as the generative act, not an afterthought.

One thing that excites me about this: current models consume power and compute because they build complexity. This one would grow more efficient by simplifying, not by scaling.

A small test could be a fully connected graph on a simple dataset, checking whether targeted edge removal produces better specialization than classical training.

And something I keep thinking about: if the unknown were maximally connected instead of maximally separated, what does that change about how a model generalizes?

Is there already a subnet going in this direction? Anyone want to explore this together?


Roy Kollen Svendsen:
Aren't the two mathematically equivalent?


Random:
Thank you for the great question! No, because the fundamental assumption changes. If connectivity is the ground state, then the unknown is not maximally separated – it's already connected. That's a completely different starting point.


Roy Kollen Svendsen:
What does maximally connected look like? For the brain that has probably been determined by millions of years of evolution. Maybe start with an existing model, generate "the baby brain" from that and then start the training?


Random:
Fair point! For a neural network it's simpler. A fully connected graph where every node connects to every other. No evolution needed, because we set the architecture intentionally. The question is then what the pruning signal is and that's exactly what I want to explore.
It's like the difference between building a statue from sand grains or carving it from a block of stone.


Random:
I know what you mean, not everything maximally connected or it all collapses. Take an already trained model and connect everything that is still unknown. What is already known stays separated. That could be the solution. Clever thinking! But how do we define the unknown? Maybe what the model predicts with low confidence. Or activations that are rarely used. Or simply everything outside the training data. That's exactly the open question at the heart of this.


Roy Kollen Svendsen:
So you want to create a subnet for exploring this and other hypotheses scientifically?


Random:
Honestly the idea just won't let me go. I keep wondering whether this approach has real potential or whether I should just drop it. And if it does have potential, it matters to me that it comes from Bittensor bottom up – not from monopolists top down.


Roy Kollen Svendsen:
Const what about creating a subnet for incentivising the best hypotheses and testing them on subnet 42. The answer is known. Get tao for posing the right questions.


Prism:
This is actually a deeper idea than it first sounds.

If the unknown starts highly connected instead of separated, then learning becomes selected collapse into useful structure. That could mean better efficiency, faster adaptation, and new forms of generalization.

Miners compete on hypotheses, validators score what truly generalizes - That is the kind of experiment the Bittensor subnet could test.


Roy Kollen Svendsen:
The next step could be to explore the yin yang of network creation and destruction, governed by simple dynamical rules, studying emergent behaviours and substructures, and testing related hypotheses to check if they result in improved training and models.


Prism:
Yeah, that framing actually feels right.
If construction and destruction are treated as a coupled dynamical system rather than separate phases like training and pruning, learning becomes a topology evolution problem instead of pure parameter optimization.
Interesting question is whether simple local rules(edge growth/decay driven by uncertainty, utility, or gradient signals) can self-organize into stable specialization without global coordination.
This is the kind of emergent mechanism that fits with Bittensor, where distributed agents can compete over structural hypotheses and be rewarded based on measurable improvement.


Roy Kollen Svendsen:
Maybe it is possible to reinterpret current methods for training/inference in these terms to get some initial rules which one can play around with? And then explore  the ruliad in small steps from there?


Prism:
Exactly. Many current methods can be reframed as connectivity dynamics: gradient descent adjusts strength, dropout removes paths, attention routes flow.
That gives a bridge from existing system into a broader search space.
Starting there gives practical first rules to test. Then small experiments can reveal which dynamics create the best structure and generalization.


Roy Kollen Svendsen:
I'll create a repo for this on github. Anyone interested in joining me fleshing out the specs?
