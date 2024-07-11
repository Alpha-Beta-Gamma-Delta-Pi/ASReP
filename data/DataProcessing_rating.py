import gzip
from collections import defaultdict
from datetime import datetime
import os
import copy
import json
import csv


def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)


countU = defaultdict(lambda: 0)
countP = defaultdict(lambda: 0)
line = 0

# DATASET = 'Beauty'
DATASET = 'Cell_Phones_and_Accessories'
dataname = 'reviews_{}_5.json.gz'.format(DATASET)
# DATASET = 'Beauty2'
DATASET += '_2'

if not os.path.isdir('./'+DATASET):
    os.mkdir('./'+DATASET)
train_file = './'+DATASET+'/train.txt'
valid_file = './'+DATASET+'/valid.txt'
test_file = './'+DATASET+'/test.txt'
imap_file = './'+DATASET+'/imap.json'
umap_file = './'+DATASET+'/umap.json'

train_reverse_file = './'+DATASET+'/train_reverse.txt'
valid_reverse_file = './'+DATASET+'/valid_reverse.txt'
test_reverse_file = './'+DATASET+'/test_reverse.txt'

usermap = dict()
usernum = 0
itemmap = dict()
itemnum = 0
User = dict()
tot_rating = 0
for l in parse(dataname):
    line += 1
    asin = l['asin']
    rev = l['reviewerID']
    time = l['unixReviewTime']
    rating = l['overall']
    #if countU[rev] < 5 or countP[asin] < 5:
    #    continue

    if rating < 3:
        continue

    tot_rating += rating

    if rev in usermap:
        userid = usermap[rev]
    else:
        userid = usernum
        usermap[rev] = userid
        User[userid] = []
        usernum += 1
    if asin in itemmap:
        itemid = itemmap[asin]
    else:
        itemid = itemnum
        itemmap[asin] = itemid
        itemnum += 1
    # if rating > 3:
    #     User[userid].append([itemid, time])
    User[userid].append([itemid, time])

# sort reviews in User according to time


with open(imap_file, 'w') as f:
    json.dump(itemmap, f)

with open(umap_file, 'w') as f:
    json.dump(usermap, f)

for userid in User.keys():
    User[userid].sort(key=lambda x: x[1])

User_forreversed = copy.deepcopy(User)
for userid in User_forreversed.keys():
    User_forreversed[userid].sort(key=lambda x: x[1], reverse=True)

print("Saved itemmap and usermap")

user_train = {}
user_valid = {}
user_test = {}
#train test val split w.r.t. no of user - item reviews
for user in User:
    nfeedback = len(User[user])
    if nfeedback < 3:
        user_train[user] = User[user]
        user_valid[user] = []
        user_test[user] = []
    else:
        user_train[user] = User[user][:-2]
        user_valid[user] = []
        user_valid[user].append(User[user][-2])
        user_test[user] = []
        user_test[user].append(User[user][-1])


user_train_reverse = {}
user_valid_reverse = {}
user_test_reverse = {}
for user in User_forreversed:
    nfeedback = len(User_forreversed[user])
    if nfeedback < 3:
        user_train_reverse[user] = User_forreversed[user]
        user_valid_reverse[user] = []
        user_test_reverse[user] = []
    else:
        user_train_reverse[user] = User_forreversed[user][:-2]
        user_valid_reverse[user] = []
        user_valid_reverse[user].append(User_forreversed[user][-2])
        user_test_reverse[user] = []
        user_test_reverse[user].append(User_forreversed[user][-1])

print(usernum, itemnum)

def writetofile(data, dfile):
    with open(dfile, 'w') as f:
        for u, ilist in sorted(data.items()):
            for i, t in ilist:
                f.write(str(u) + '\t'+ str(i) + '\t' + str(t) + "\n")

                # def write_dict_to_csv(data, filename):
                #     with open(filename, 'w', newline='') as csvfile:
                #         writer = csv.writer(csvfile)
                #         writer.writerow(['user', 'item', 'time'])
                #         for user, ilist in sorted(data.items()):
                #             for item, time in ilist:
                #                 writer.writerow([user, item, time])

                # write_dict_to_csv(user_train, train_file)
                # write_dict_to_csv(user_valid, valid_file)
                # write_dict_to_csv(user_test, test_file)
                # write_dict_to_csv(user_train_reverse, train_reverse_file)
                # write_dict_to_csv(user_valid_reverse, valid_reverse_file)
                # write_dict_to_csv(user_test_reverse, test_reverse_file)

writetofile(user_train, train_file)
writetofile(user_valid, valid_file)
writetofile(user_test, test_file)


writetofile(user_train_reverse, train_reverse_file)
writetofile(user_valid_reverse, valid_reverse_file)
writetofile(user_test_reverse, test_reverse_file)

num_instances = sum([len(ilist) for _, ilist in User.items()])
print('total user: ', len(User))
print('total instances: ', num_instances)
print('average rating: ', tot_rating/num_instances)
print('total items: ', itemnum)
print('density: ', num_instances / (len(User) * itemnum))
print('valid #users: ', len(user_valid))
numvalid_instances = sum([len(ilist) for _, ilist in user_valid.items()])
print('valid instances: ', numvalid_instances)
numtest_instances = sum([len(ilist) for _, ilist in user_test.items()])
print('test #users: ', len(user_test))
print('test instances: ', numtest_instances)
