# Deep Learning Systems Portfolio: Classification, Generation, and Domain Adaptation

This repository consolidates six graduate-level machine learning and deep learning projects into one structured portfolio for Applied AI Engineer / Machine Learning Engineer roles.

The project demonstrates a progression from classical machine learning to neural networks, optimization techniques, convolutional vision models, generative modeling, and domain adaptation. The main goal is to show not only model usage, but also hands-on understanding of training pipelines, loss functions, backpropagation, regularization, evaluation, and transfer across data distributions.

## Project Narrative

This portfolio follows one learning and engineering arc:

```text
Classical ML -> Neural Networks from Scratch -> Optimization -> CNNs -> GANs -> Domain Adaptation
```

In interview terms, the strongest project story is:

> I built a structured deep learning systems portfolio covering multiple learning paradigms. I began with classical regression and classification methods, then implemented neural networks from scratch to understand how forward propagation, loss computation, backpropagation, and parameter updates work. I then improved model training with dropout, batch normalization, mini-batch training, and Adam-style optimization. Finally, I implemented PyTorch-based CNN, GAN, and domain-adversarial learning models, including a gradient reversal layer for source-to-target domain adaptation.

## Module Overview

| Module | Focus | Key Implementation | Result / Evidence |
|---|---|---|---|
| 1. [Classical ML Foundations](notebooks/01-classical-ml-foundations/README.md) | Polynomial linear regression, ridge regression, k-fold cross-validation, logistic regression, gradient descent | poly_transform, lin_reg_obj, lin_reg_fit, get_rmse, ridge_reg_fit... | Regression and classification pipeline implemented from scratch; note: the uploaded notebook still contains one stale error output and should be rerun before public release. |
| 2. [Neural Network from Scratch](notebooks/02-neural-network-from-scratch/README.md) | ReLU, softmax cross-entropy, forward propagation, backpropagation, parameter updates, MNIST classification | relu, relu_der, linear, linear_der, softmax_cross_entropy_loss... | MNIST subset: cost decreased from 2.303 to around 0.158; training accuracy 97.25%; testing accuracy 90.80%. |
| 3. [Neural Network Optimization Techniques](notebooks/03-neural-network-optimization/README.md) | Dropout, batch normalization, mini-batch training, momentum/Adam-style optimization, learning-rate decay | dropout, dropout_der, batchnorm, batchnorm_der, initialize_velocity... | MNIST full dataset: network reached 96.748% training accuracy and 96.170% testing accuracy. |
| 4. [CNN Image Classification](notebooks/04-cnn-image-classification/README.md) | Convolutional layers, batch normalization, ReLU, pooling, fully connected layers, PyTorch training/evaluation loops | Model, train_model, evaluate_model | CNN achieved 94.506% train accuracy and 91.000% test accuracy. |
| 5. [GAN Image Generation](notebooks/05-gan-image-generation/README.md) | Generator, discriminator, binary cross-entropy loss, adversarial training, qualitative image generation | noise, Generator, Discriminator, DLoss, GLoss | Trained a GAN with adversarial generator/discriminator losses; generated samples were tracked qualitatively across epochs. |
| 6. [Domain-Adversarial Neural Network](notebooks/06-domain-adversarial-learning/README.md) | Feature extractor, label classifier, domain classifier, gradient reversal, source-to-target transfer | FeatureExtractor, LabelClassifier, GradReverse, DomainClassifier, calc_clf_logits... | Source-only model: source test 94.11%, target test 57.17%. With DANN: source test 85.90%, target test 62.09%, improving target-domain generalization by 4.92 percentage points. |

## Key Technical Skills Demonstrated

- Machine learning fundamentals: linear regression, ridge regression, logistic regression, cross-validation, RMSE, binary cross-entropy
- Neural network fundamentals: forward propagation, backpropagation, activation functions, gradient descent, softmax cross-entropy
- Optimization and regularization: dropout, batch normalization, mini-batch training, momentum/Adam-style updates, learning-rate decay
- Computer vision: CNNs, convolutional layers, pooling, PyTorch training loops, model evaluation
- Generative modeling: GAN generator/discriminator architecture, adversarial loss, qualitative image generation
- Domain adaptation: domain-adversarial neural networks, gradient reversal, domain-invariant representation learning
- Engineering workflow: reproducible notebooks, modular source extraction, model evaluation, experiment documentation

## Repository Structure

```text
deep-learning-systems-portfolio/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   ├── 01-classical-ml-foundations/
│   ├── 02-neural-network-from-scratch/
│   ├── 03-neural-network-optimization/
│   ├── 04-cnn-image-classification/
│   ├── 05-gan-image-generation/
│   └── 06-domain-adversarial-learning/
├── src/
│   ├── module_01_classical_ml_foundations.py
│   ├── module_02_neural_network_from_scratch.py
│   ├── module_03_neural_network_optimization.py
│   ├── module_04_cnn_image_classification.py
│   ├── module_05_gan_image_generation.py
│   └── module_06_domain_adversarial_learning.py
└── docs/
    ├── RESUME_BULLETS.md
    ├── INTERVIEW_GUIDE.md
    ├── LEARNING_GUIDE_ZH.md
    └── PROJECT_STORY.md
```

## How to Run

1. Create a Python environment.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Open the notebooks.

```bash
jupyter notebook
```

3. Run modules individually. Some notebooks depend on local datasets or course-provided helper files stored inside each module folder. If data files are not present or are zero-byte placeholders, re-download the dataset or use the course-provided data source before rerunning training.

## Important Portfolio Note

These notebooks were originally completed as coursework. Before publishing publicly, review your university/course academic integrity policy. A safer public GitHub version may keep high-level implementation summaries, selected snippets, and results while avoiding full release of course-specific solutions.

## Resume Positioning

This project is best positioned as an **ML/DL foundation project** for Applied AI Engineer roles. It proves strong understanding of model training, optimization, and evaluation. For modern LLM-focused Applied AI roles, pair this portfolio with a separate RAG/Agent/LLM product project.
