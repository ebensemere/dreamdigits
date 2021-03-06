# libraries!
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

filename = 'digits.csv'
df = pd.read_csv(filename, header=0)
print(f"{filename} : file read into a pandas dataframe.")

coltodrop = df.columns[65]
df_clean = df.drop(columns=[coltodrop])
df_clean.info()

COLUMNS = df_clean.columns
print(f"COLUMNS: {COLUMNS}")

# let's create a dictionary to look up any column index by name
COL_INDEX = {}
for i, name in enumerate(COLUMNS):
    COL_INDEX[name] = i  # using the name (as key), look up the value (i)
print(f"COL_INDEX: {COL_INDEX}")

# and for our "SPECIES"!
SPECIES = [str(i) for i in range(0, 10)]  # list with a string at each index (index -> string)
SPECIES_INDEX = {s: int(s) for s in SPECIES}  # dictionary mapping from string -> index

A = df_clean.to_numpy()  # .values gets the numpy array
A = A.astype('float64')  # so many:  www.tutorialspoint.com/numpy/numpy_data_types.htm

#
# regression model that uses as input the first 48 pixels (pix0 to pix47)
#                       and, as output, predicts the value of pix52
#

print("+++ Start of regression prediction of pix52! +++\n")

X_all = A[:, 0:48]  # old: np.concatenate( (A[:,0:3], A[:,4:]),axis=1)  # horizontal concatenation
y_all = A[:, 52]  # y (labels) ... is all rows, column indexed 52 (pix52) only (actually the 53rd pixel, but ok)

print(f"y_all (just target values, pix52)   is \n {y_all}")
print(f"X_all (just features: 3 rows) is \n {X_all[:3, :]}")

#
# we scramble the data, to give a different TRAIN/TEST split each time...
#
indices = np.random.permutation(len(y_all))  # indices is a permutation-list

# we scramble both X and y, necessarily with the same permutation
X_all = X_all[indices]  # we apply the _same_ permutation to each!
y_all = y_all[indices]  # again...
print("labels (target)\n", y_all)
print("features\n", X_all[:3, :])

#
# We next separate into test data and training data ...
#    + We will train on the training data...
#    + We will _not_ look at the testing data to build the model
#
# Then, afterward, we will test on the testing data -- and see how well we do!
#

#
# a common convention:  train on 80%, test on 20%    Let's define the TEST_PERCENT
#


X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=0.2)

print(f"training with {len(y_train)} rows;  testing with {len(y_test)} rows\n")

print(f"Held-out data... (testing data: {len(y_test)})")
print(f"y_test: {y_test}\n")
print(f"X_test (few rows): {X_test[0:5, :]}")  # 5 rows
print()
print(f"Data used for modeling... (training data: {len(y_train)})")
print(f"y_train: {y_train}\n")
print(f"X_train (few rows): {X_train[0:5, :]}")  # 5 rows

#
# for NNets, it's important to keep the feature values near 0, say -1. to 1. or so
#    This is done through the "StandardScaler" in scikit-learn
#
USE_SCALER = True  # this variable is important! It tracks if we need to use the scaler...

# we "train the scaler"  (computes the mean and standard deviation)
if USE_SCALER:
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    scaler.fit(X_train)  # Scale with the training data! ave becomes 0; stdev becomes 1
else:
    # this one does no scaling!  We still create it to be consistent:
    scaler = StandardScaler(copy=True, with_mean=False, with_std=False)  # no scaling
    scaler.fit(X_train)  # still need to fit, though it does not change...

scaler  # is now defined and ready to use...

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Here is a fully-scaled dataset:

X_all_scaled = scaler.transform(X_all)
y_all_scaled = y_all.copy()  # not scaled

# Here are our scaled training and testing sets:

X_train_scaled = scaler.transform(X_train)  # scale!
X_test_scaled = scaler.transform(X_test)  # scale!

y_train_scaled = y_train  # the predicted/desired labels are not scaled
y_test_scaled = y_test  # not using the scaler


def ascii_table(X, y):
    """ print a table of binary inputs and outputs """
    print(f"{'input ':>70s} -> {'pred':<5s} {'des.':<5s}")
    for i in range(len(y)):
        s_to_show = str(X[i, :])
        s_to_show = s_to_show[0:60]
        print(f"{s_to_show!s:>70s} -> {'?':<5s} {y[i]:<5.0f}")  # !s is str ...


ascii_table(X_train_scaled[0:5, :], y_train_scaled[0:5])

#
# Note that the zeros have become -1's
# and the 1's have stayed 1's
#

#
# MLPRegressor predicts _floating-point_ outputs
#



nn_regressor = MLPRegressor(hidden_layer_sizes=(6, 7),
                            max_iter=200,  # how many training epochs
                            activation="tanh",  # the activation function
                            solver='sgd',  # the optimizer
                            verbose=True,  # do we want to watch as it trains?
                            shuffle=True,  # shuffle each epoch?
                            random_state=None,  # use for reproducibility
                            learning_rate_init=.1,  # how much of each error to back-propagate
                            learning_rate='adaptive')  # how to handle the learning_rate

print("\n\n++++++++++  TRAINING:  begin  +++++++++++++++\n\n")
nn_regressor.fit(X_train_scaled, y_train_scaled)
print("++++++++++  TRAINING:   end  +++++++++++++++")

print(f"The (squared) prediction error (the loss) is {nn_regressor.loss_}")
print(f"And, its square root: {nn_regressor.loss_ ** 0.5}")


def ascii_table_for_regressor(Xsc, y, nn, scaler):
    """ a table including predictions using nn.predict """
    predictions = nn.predict(Xsc)  # all predictions
    Xpr = scaler.inverse_transform(Xsc)  # Xpr is the "X to print": unscaled data!
    # measure error
    error = 0.0
    # printing
    print(f"{'input ':>35s} ->  {'pred':^6s}  {'des.':^6s}  {'absdiff':^10s}")
    for i in range(len(y)):
        pred = predictions[i]
        desired = y[i]
        result = abs(desired - pred)
        error += result
        # Xpr = Xsc   # if you'd like to see the scaled values
        s_to_show = str(Xpr[i, :])
        s_to_show = s_to_show[0:25]  # we'll just take 25 of these
        print(f"{s_to_show!s:>35s} ->  {pred:<+6.3f}  {desired:<+6.3f}  {result:^10.3f}")

    print("\n" + "+++++   +++++      +++++   +++++   ")
    print(f"average abs error: {error / len(y)}")
    print("+++++   +++++      +++++   +++++   ")


if True:
    ascii_table_for_regressor(X_test_scaled,
                              y_test_scaled,
                              nn_regressor,
                              scaler)  # this is our own f'n, above

# let's create a final nn_regressor for pix52
#
pix52_final_regressor = MLPRegressor(hidden_layer_sizes=(6, 7),
                                     max_iter=400,
                                     activation="tanh",
                                     solver='sgd',
                                     verbose=False,
                                     shuffle=True,
                                     random_state=None,  # reproduceability!
                                     learning_rate_init=.1,
                                     learning_rate='adaptive')

print("\n\n++++++++++  TRAINING:  begin  +++++++++++++++\n\n")
pix52_final_regressor.fit(X_all_scaled, y_all_scaled)
print("\n\n++++++++++  TRAINING:   end  +++++++++++++++\n\n")

print(f"The (sq) prediction error (the loss) is {pix52_final_regressor.loss_}")
print(f"So, the 'average' error per pixel is {pix52_final_regressor.loss_ ** 0.5}")


def predict_from_model(pixels, model):
    """ returns the prediction on the input pixels using the input model
    """
    pixels_array = np.asarray([pixels])  # the extra sq. brackets are needed!
    pixels_scaled = scaler.transform(pixels_array)  # need to use the scaler!
    predicted = model.predict(pixels_scaled)
    return predicted


#
# let's choose a digit to try...
#
row_to_show = 4  # different indexing from X_all and y_all (they were reordered)
numeral = A[row_to_show, 64]
print(f"The numeral is a {int(numeral)}\n")

all_pixels = A[row_to_show, 0:64]
first48pixels = A[row_to_show, 0:48]

pix52_predicted = predict_from_model(first48pixels, pix52_final_regressor)
pix52_actual = A[row_to_show, 52]

print(f"pix52 [predicted] vs. actual:  {pix52_predicted} vs. {pix52_actual}")


def show_digit(pixels):
    """ should create a heatmap (image) of the digit contained in row
            input: pixels should be a 1d numpy array
            if it's more then 64 values, it will be truncated
            if it's fewer than 64 values, 0's will be appended

    """
    # make sure the sizes are ok!
    num_pixels = len(pixels)
    if num_pixels != 64:
        print(f"(in show_digit) num_pixels was {num_pixels}; now set to 64")
    if num_pixels > 64:  # an elif would be a poor choice here, as I found!
        pixels = pixels[0:64]
    if num_pixels < 64:
        num_zeros = 64 - len(pixels)
        pixels = np.concatenate((pixels, np.zeros(num_zeros)), axis=0)

    pixels = pixels.astype(int)  # convert to integers for plotting
    pixels = np.reshape(pixels, (8, 8))  # make 8x8
    # print(f"The pixels are\n{pixels}")
    f, ax = plt.subplots(figsize=(9, 6))  # Draw a heatmap w/option of numeric values in each cell

    # my_cmap = sns.dark_palette("Purple", as_cmap=True)
    my_cmap = sns.light_palette("Gray",
                                as_cmap=True)
    sns.heatmap(pixels, annot=False, fmt="d", linewidths=.5, ax=ax, cmap=my_cmap)



row_to_show = 42
numeral = A[row_to_show, 64]
print(f"The numeral is a {int(numeral)}\n")
# show all from the original data
show_digit(A[row_to_show, 0:64])  # show full original


all_pixels = A[row_to_show, 0:64].copy()
first48pixels = all_pixels[0:48]
show_digit(all_pixels)

pix52_predicted = predict_from_model(first48pixels, pix52_final_regressor)
pix52_actual = A[row_to_show, 52]

print(f"pix52 [predicted] vs. actual:  {pix52_predicted} {pix52_actual}")

# erase last 16 pixels
all_pixels[48:64] = np.zeros(16)

# show without pix52
all_pixels[52] = 0  # omit this one
show_digit(all_pixels)  # show without pixel 52

# show with pix52
all_pixels[52] = np.round(pix52_predicted)  # include this one
show_digit(all_pixels)  # show with pixel 52


def make_r(N):
    R = []
    X_all = A[:, 0:N]


    scaler = StandardScaler()
    scaler.fit(X_train)
    X_all_scaled = scaler.transform(X_all)

    for value in range(N, 64):
        print(value)
        y_all = A[:, value]
        y_all_scaled = y_all.copy()
        pix_final_regressor = MLPRegressor(hidden_layer_sizes=(6, 7),
                                           max_iter=400,
                                           activation="tanh",
                                           solver='sgd',
                                           verbose=False,
                                           shuffle=True,
                                           random_state=None,
                                           learning_rate_init=.1,
                                           learning_rate='adaptive')
        pix_final_regressor.fit(X_all_scaled, y_all_scaled)
        R += [pix_final_regressor]

    return R


row_to_show = 42
numeral = A[row_to_show, 64]
print(f"The numeral is a {int(numeral)}\n")

all_pixels = A[row_to_show, 0:64].copy()
first48pixels = all_pixels[0:48]

pix52_predicted = predict_from_model(first48pixels, pix52_final_regressor)
pix52_actual = A[row_to_show, 52]

print(f"pix52 [predicted] vs. actual:  {pix52_predicted} {pix52_actual}")

# erase last 16 pixels
all_pixels[48:64] = np.zeros(16)

# show without pix52
all_pixels[52] = 0  # omit this one
show_digit(all_pixels)  # show without pixel 52

# show with pix52
all_pixels[52] = np.round(pix52_predicted)  # include this one
show_digit(all_pixels)  # show without pixel 52

row_to_show = 42  # different indexing from X_all and y_all (they were reordered)
numeral = A[row_to_show, 64]
print(f"The numeral is a {int(numeral)}\n")

all_pixels = A[row_to_show, 0:64].copy()
first_pixels = all_pixels[0:48]  # should be 32!

pix52_predicted = predict_from_model(first_pixels, pix52_final_regressor)
pix52_actual = A[row_to_show, 52]

print(f"pix52 [predicted] vs. actual:  {pix52_predicted} {pix52_actual}")

# erase last 32 pixels
all_pixels[32:64] = np.zeros(32)
show_digit(all_pixels)

# set pix52
all_pixels[52] = np.round(pix52_predicted)
show_digit(all_pixels)


def predict_digit(R, row_to_show):
    numeral = A[row_to_show, 64]
    print(f"The numeral is a {int(numeral)}\n")
    show_digit(A[row_to_show, 0:64])

    all_pixels = A[row_to_show, 0:64].copy()
    first48pixels = all_pixels[0:48]

    all_pixels[48:64] = np.zeros(16)
    show_digit(all_pixels)

    for value in range(48, 64):
        r = R[(value - 48)]
        pix_predicted = predict_from_model(first48pixels, r)
        pix_actual = A[row_to_show, value]
        print(f"pix{value} [predicted] vs. actual:  {pix_predicted} {pix_actual}")
        all_pixels[value] = np.round(pix_predicted)
    show_digit(all_pixels)


R = make_r(48)
predict_digit(R, 75)
