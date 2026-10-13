# Candidate Evidence Gold v2 — Deep Learning README

**Review status:** HUMAN_REVIEWED (author-confirmed for Portfolio V1; historical analysis preserved).

**Document:** `README._deeplearning.md`

## Annotation policy

- Include implemented work, technical methods actually used, evaluation activities, measured outcomes, and useful engineering workflow evidence.
- Exclude document/repository metadata, role-positioning statements, future plans, setup instructions, and generic “this demonstrates” claims by default.
- Prefer atomic evidence units. Separate implementation from measured outcomes when both are independently useful for downstream job matching.

## Draft evidence units (12)

### G001
**Claim:** Implemented a classical regression and classification pipeline from scratch, including polynomial regression, ridge regression, cross-validation, logistic regression, and gradient descent.

**Source section:** Module Overview — Classical ML Foundations

**Source text:**

> | 1. [Classical ML Foundations](notebooks/01-classical-ml-foundations/README.md) | Polynomial linear regression, ridge regression, k-fold cross-validation, logistic regression, gradient descent | poly_transform, lin_reg_obj, lin_reg_fit, get_rmse, ridge_reg_fit... | Regression and classification pipeline implemented from scratch; note: the uploaded notebook still contains one stale error output and should be rerun before public release. |

### G002
**Claim:** Implemented a neural network from scratch with ReLU, softmax cross-entropy, forward propagation, backpropagation, and parameter updates.

**Source section:** Module Overview — Neural Network from Scratch

**Source text:**

> | 2. [Neural Network from Scratch](notebooks/02-neural-network-from-scratch/README.md) | ReLU, softmax cross-entropy, forward propagation, backpropagation, parameter updates, MNIST classification | relu, relu_der, linear, linear_der, softmax_cross_entropy_loss... | MNIST subset: cost decreased from 2.303 to around 0.158; training accuracy 97.25%; testing accuracy 90.80%. |

### G003
**Claim:** Achieved 97.25% training accuracy and 90.80% testing accuracy on an MNIST subset with the neural-network-from-scratch implementation.

**Source section:** Module Overview — Neural Network from Scratch

**Source text:**

> | 2. [Neural Network from Scratch](notebooks/02-neural-network-from-scratch/README.md) | ReLU, softmax cross-entropy, forward propagation, backpropagation, parameter updates, MNIST classification | relu, relu_der, linear, linear_der, softmax_cross_entropy_loss... | MNIST subset: cost decreased from 2.303 to around 0.158; training accuracy 97.25%; testing accuracy 90.80%. |

### G004
**Claim:** Implemented neural-network optimization techniques including dropout, batch normalization, mini-batch training, momentum/Adam-style optimization, and learning-rate decay.

**Source section:** Module Overview — Neural Network Optimization Techniques

**Source text:**

> | 3. [Neural Network Optimization Techniques](notebooks/03-neural-network-optimization/README.md) | Dropout, batch normalization, mini-batch training, momentum/Adam-style optimization, learning-rate decay | dropout, dropout_der, batchnorm, batchnorm_der, initialize_velocity... | MNIST full dataset: network reached 96.748% training accuracy and 96.170% testing accuracy. |

### G005
**Claim:** Reached 96.748% training accuracy and 96.170% testing accuracy on the full MNIST dataset after applying the optimization techniques.

**Source section:** Module Overview — Neural Network Optimization Techniques

**Source text:**

> | 3. [Neural Network Optimization Techniques](notebooks/03-neural-network-optimization/README.md) | Dropout, batch normalization, mini-batch training, momentum/Adam-style optimization, learning-rate decay | dropout, dropout_der, batchnorm, batchnorm_der, initialize_velocity... | MNIST full dataset: network reached 96.748% training accuracy and 96.170% testing accuracy. |

### G006
**Claim:** Built a PyTorch CNN image-classification pipeline using convolutional layers, batch normalization, ReLU, pooling, fully connected layers, and training/evaluation loops.

**Source section:** Module Overview — CNN Image Classification

**Source text:**

> | 4. [CNN Image Classification](notebooks/04-cnn-image-classification/README.md) | Convolutional layers, batch normalization, ReLU, pooling, fully connected layers, PyTorch training/evaluation loops | Model, train_model, evaluate_model | CNN achieved 94.506% train accuracy and 91.000% test accuracy. |

### G007
**Claim:** Achieved 94.506% training accuracy and 91.000% test accuracy with the CNN image-classification model.

**Source section:** Module Overview — CNN Image Classification

**Source text:**

> | 4. [CNN Image Classification](notebooks/04-cnn-image-classification/README.md) | Convolutional layers, batch normalization, ReLU, pooling, fully connected layers, PyTorch training/evaluation loops | Model, train_model, evaluate_model | CNN achieved 94.506% train accuracy and 91.000% test accuracy. |

### G008
**Claim:** Implemented and trained a GAN with generator and discriminator architectures, binary cross-entropy loss, and adversarial training.

**Source section:** Module Overview — GAN Image Generation

**Source text:**

> | 5. [GAN Image Generation](notebooks/05-gan-image-generation/README.md) | Generator, discriminator, binary cross-entropy loss, adversarial training, qualitative image generation | noise, Generator, Discriminator, DLoss, GLoss | Trained a GAN with adversarial generator/discriminator losses; generated samples were tracked qualitatively across epochs. |

### G009
**Claim:** Tracked generated GAN samples qualitatively across training epochs.

**Source section:** Module Overview — GAN Image Generation

**Source text:**

> | 5. [GAN Image Generation](notebooks/05-gan-image-generation/README.md) | Generator, discriminator, binary cross-entropy loss, adversarial training, qualitative image generation | noise, Generator, Discriminator, DLoss, GLoss | Trained a GAN with adversarial generator/discriminator losses; generated samples were tracked qualitatively across epochs. |

### G010
**Claim:** Implemented a domain-adversarial neural network using a feature extractor, label classifier, domain classifier, and gradient reversal for source-to-target domain adaptation.

**Source section:** Module Overview — Domain-Adversarial Neural Network

**Source text:**

> | 6. [Domain-Adversarial Neural Network](notebooks/06-domain-adversarial-learning/README.md) | Feature extractor, label classifier, domain classifier, gradient reversal, source-to-target transfer | FeatureExtractor, LabelClassifier, GradReverse, DomainClassifier, calc_clf_logits... | Source-only model: source test 94.11%, target test 57.17%. With DANN: source test 85.90%, target test 62.09%, improving target-domain generalization by 4.92 percentage points. |

### G011
**Claim:** Improved target-domain test performance from 57.17% with the source-only model to 62.09% with DANN, a 4.92 percentage-point improvement.

**Source section:** Module Overview — Domain-Adversarial Neural Network

**Source text:**

> | 6. [Domain-Adversarial Neural Network](notebooks/06-domain-adversarial-learning/README.md) | Feature extractor, label classifier, domain classifier, gradient reversal, source-to-target transfer | FeatureExtractor, LabelClassifier, GradReverse, DomainClassifier, calc_clf_logits... | Source-only model: source test 94.11%, target test 57.17%. With DANN: source test 85.90%, target test 62.09%, improving target-domain generalization by 4.92 percentage points. |

### G012
**Claim:** Used an engineering workflow involving reproducible notebooks, modular source extraction, model evaluation, and experiment documentation.

**Source section:** Key Technical Skills Demonstrated

**Source text:**

> - Engineering workflow: reproducible notebooks, modular source extraction, model evaluation, experiment documentation
