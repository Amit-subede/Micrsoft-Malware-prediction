#%%
import random
import os
import shutil
import codecs
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import scipy.stats as stats
from tqdm import tqdm
import imageio
import array

sns.set()

#%%
class shift_files:
    def __init__(self):
        source = 'train'
        destination_1 = 'byteFiles'
        destination_2 = 'asmFiles'

        if not os.path.isdir(destination_1):
            os.makedirs(destination_1)
        if not os.path.isdir(destination_2):
            os.makedirs(destination_2)

        self.source = source
        self.destination_1 = destination_1
        self.destination_2 = destination_2

    @staticmethod
    def process(source, destination_1, destination_2):
        if os.path.isdir(source):
            data_files = os.listdir(source)
            asm_files = {}
            bytes_files = {}

            for file in data_files:
                if file.endswith(".asm"):
                    asm_files[file.split('.')[0]] = file
                elif file.endswith(".bytes"):
                    bytes_files[file.split('.')[0]] = file

            #selected_bytes_keys = random.sample(list(bytes_files.keys()), 3000)

            #For same sampling for the runner, saved the ids used
            ids_selected = pd.read_csv('IDS_selected.csv')
            ids_selected = ids_selected['ID'].to_list()
            selected_bytes_keys = ids_selected

            for key in selected_bytes_keys:
                asm_file = asm_files.get(key + ".asm")
                if asm_file:
                    shutil.move(os.path.join(source, bytes_files[key]), destination_1)
                    shutil.move(os.path.join(source, asm_file), destination_2)
        else:
            print("Please keep source file named 'train' in the same folder as the runner. Download link \
                  https://www.kaggle.com/competitions/malware-classification/data")

    def execute(self):
        shift_files.process(self.source, self.destination_1, self.destination_2)

# Creating an instance of the class and executing the process
shift_files_instance = shift_files()
shift_files_instance.execute()


#%%
class ByteFileProcessor:
    @staticmethod
    def process_byte_files():
        files = os.listdir('byteFiles')
        filenames = []
        feature_matrix = np.zeros((len(files), 257), dtype=int)
        k = 0

        byte_feature_file = open('byteoutputfile.csv', 'w+')
        byte_feature_file.write("ID,0,1,2,3,4,5,6,7,8,9,0a,0b,0c,0d,0e,0f,10,11,12,13,14,15,16,17,18,19,1a,1b,1c,1d,1e,1f,20,21,22,23,24,25,26,27,28,29,2a,2b,2c,2d,2e,2f,30,31,32,33,34,35,36,37,38,39,3a,3b,3c,3d,3e,3f,40,41,42,43,44,45,46,47,48,49,4a,4b,4c,4d,4e,4f,50,51,52,53,54,55,56,57,58,59,5a,5b,5c,5d,5e,5f,60,61,62,63,64,65,66,67,68,69,6a,6b,6c,6d,6e,6f,70,71,72,73,74,75,76,77,78,79,7a,7b,7c,7d,7e,7f,80,81,82,83,84,85,86,87,88,89,8a,8b,8c,8d,8e,8f,90,91,92,93,94,95,96,97,98,99,9a,9b,9c,9d,9e,9f,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,aa,ab,ac,ad,ae,af,b0,b1,b2,b3,b4,b5,b6,b7,b8,b9,ba,bb,bc,bd,be,bf,c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,ca,cb,cc,cd,ce,cf,d0,d1,d2,d3,d4,d5,d6,d7,d8,d9,da,db,dc,dd,de,df,e0,e1,e2,e3,e4,e5,e6,e7,e8,e9,ea,eb,ec,ed,ee,ef,f0,f1,f2,f3,f4,f5,f6,f7,f8,f9,fa,fb,fc,fd,fe,ff,??")
        byte_feature_file.write("\n")

        for file in files:
            filenames.append(file)
            byte_feature_file.write(file + ",")
            if file.endswith("txt"):
                with open('byteFiles/' + file, "r") as byte_file:
                    for lines in byte_file:
                        line = lines.rstrip().split(" ")
                        for hex_code in line:
                            if hex_code == '??':
                                feature_matrix[k][256] += 1
                            else:
                                feature_matrix[k][int(hex_code, 16)] += 1

            for i, row in enumerate(feature_matrix[k]):
                if i != len(feature_matrix[k]) - 1:
                    byte_feature_file.write(str(row) + ",")
                else:
                    byte_feature_file.write(str(row))
            byte_feature_file.write("\n")

            k += 1

        byte_feature_file.close()


ByteFileProcessor.process_byte_files()


#%%
class AsmFileProcessor:
    
    @staticmethod
    def firstprocess():
        prefixes = ['HEADER:', '.text:', '.Pav:', '.idata:', '.data:', '.bss:', '.rdata:', '.edata:', '.rsrc:', '.tls:', '.reloc:', '.BSS:', '.CODE']
        opcodes = ['jmp', 'mov', 'retf', 'push', 'pop', 'xor', 'retn', 'nop', 'sub', 'inc', 'dec', 'add', 'imul', 'xchg', 'or', 'shr', 'cmp', 'call', 'shl', 'ror', 'rol', 'jnb', 'jz', 'rtn', 'lea', 'movzx']
        keywords = ['.dll', 'std::', ':dword']
        registers = ['edx', 'esi', 'eax', 'ebx', 'ecx', 'edi', 'ebp', 'esp', 'eip']

        asm_output_file = open("asmoutputfile.csv", "w+")  
        files = os.listdir('asmfiles')

        for f in files:
            prefixescount = np.zeros(len(prefixes), dtype=int)
            opcodescount = np.zeros(len(opcodes), dtype=int)
            keywordcount = np.zeros(len(keywords), dtype=int)
            registerscount = np.zeros(len(registers), dtype=int)
            features = []
            f2 = f.split('.')[0]
            asm_output_file.write(f2 + ",")
            
            with codecs.open('asmfiles/' + f, encoding='cp1252', errors='replace') as fli:
                for lines in fli:
                    line = lines.rstrip().split()
                    l = line[0]
                    
                    for i in range(len(prefixes)):
                        if prefixes[i] in line[0]:
                            prefixescount[i] += 1
                    
                    line = line[1:]
                    
                    for i in range(len(opcodes)):
                        if any(opcodes[i] == li for li in line):
                            features.append(opcodes[i])
                            opcodescount[i] += 1
                    
                    for i in range(len(registers)):
                        for li in line:
                            if registers[i] in li and ('text' in l or 'CODE' in l):
                                registerscount[i] += 1
                    
                    for i in range(len(keywords)):
                        for li in line:
                            if keywords[i] in li:
                                keywordcount[i] += 1
            
            for prefix in prefixescount:
                asm_output_file.write(str(prefix) + ",")
            for opcode in opcodescount:
                asm_output_file.write(str(opcode) + ",")
            for register in registerscount:
                asm_output_file.write(str(register) + ",")
            for key in keywordcount:
                asm_output_file.write(str(key) + ",")
            asm_output_file.write("\n")
        
        asm_output_file.close()

    @staticmethod
    def main():
        AsmFileProcessor.firstprocess()

AsmFileProcessor.main()


#%%
asm_file = pd.read_csv('asmoutputfile.csv')
byte_file = pd.read_csv('byteoutputfile.csv')

#removing ".txt" forom ids of byte file
byte_file['ID'] = byte_file['ID'].apply(lambda x : x[:-4])

labels = pd.read_csv('trainLabels.csv').rename(columns = {'Id' : "ID"})


#%%
byte_cols = byte_file.columns.to_list()
asm_cols = asm_file.columns.to_list()

print(len(byte_cols) - 1 , 'Unigram byte features')
print(len(asm_cols) - 1 ,  'Unigram asm features')

def make_box_labels(Y):
    total = len(Y)*1.
    ax=sns.countplot(x="Class", data=Y)

    ax.set_title("Distribution of Labels")
    #ax.set_grid()
    for p in ax.patches:
            ax.annotate('{:.1f}%'.format(100*p.get_height()/total), (p.get_x()+0.1, p.get_height()+5))

    ax.yaxis.set_ticks(np.linspace(0, total, 11))

    ax.set_yticklabels(map('{:.1f}%'.format, 100*ax.yaxis.get_majorticklocs()/total))

    plt.grid()
    plt.show()


final_df = byte_file.merge(asm_file , on = "ID" , how = "inner")
final_df = final_df.merge(labels , on = 'ID' , how = 'inner')
make_box_labels(final_df[["ID" , 'Class']])


#%%
class Analysis:

    def __init__(self):
        pass
    

    @staticmethod
    def normalize(df , columns):
        result1 = df.copy()
        for feature_name in columns:
            if (str(feature_name) != str('ID') and str(feature_name)!=str('Class')):
                max_value = df[feature_name].max()
                min_value = df[feature_name].min()
                result1[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
        return result1
    

    @staticmethod
    def get_Tsne_plot(result , val , data_y , type_):


        xtsne=TSNE(perplexity=val)
        result = xtsne.fit_transform(result.drop(['ID'], axis=1))
        vis_x = result[:, 0]
        vis_y = result[:, 1]

        plt.title("T-SNE Dist plot for " + type_)
        plt.scatter(vis_x, vis_y, c=data_y, cmap=plt.cm.get_cmap("jet", 9))
        plt.colorbar(ticks=range(10))
        plt.clim(0.5, 9)
        plt.show()

    @staticmethod
    def get_counts(df):

        df_bytes = df.select_dtypes(include='int64').sum(axis = 0)
        df_bytes['Class'] = df['Class'].max()

        return df_bytes

    @staticmethod
    def get_probs(final_df , asm_cols , byte_cols):
        
        if "ID" in asm_cols:
            asm_cols.remove('ID')
        if "ID" in byte_cols:
            byte_cols.remove('ID')

        counts_df = final_df.groupby('Class').apply(Analysis.get_counts)

        byte_counts = counts_df[byte_cols[:]].sum(axis = 1)
        asm_counts = counts_df[asm_cols[:]].sum(axis = 1)

        bytes_probs = counts_df[byte_cols[:]].div(byte_counts.values , axis = 0).T
        asm_probs = counts_df[asm_cols[:]].div(asm_counts.values , axis = 0).T

        return bytes_probs , asm_probs

    @staticmethod
    def compare_dists(df):
        distributions = ['norm','bernoulli']


        fig, axes = plt.subplots(nrows=9, ncols=2, figsize=(10, 30))

        for i, column in enumerate(df.columns):
            for j, distribution in enumerate(distributions):
                ax = axes[i][j]
                if distribution == 'norm':
                    stats.probplot(df[column], dist=distribution, plot=ax)
                    ax.set_title(f'{column} - {distribution.capitalize()}')
                elif distribution == 'bernoulli':
                    # For Bernoulli, generate quantiles for the empirical distribution
                    quantiles = df[column].rank(pct=True)
                    stats.probplot(quantiles, dist='uniform', plot=ax)
                    ax.set_title(f'{column} - Empirical vs Uniform')
                
                ax.grid(True)

        plt.tight_layout()
        plt.show()



#%%
data_y = final_df.Class
byte_data = Analysis.normalize(final_df , byte_cols)
Analysis.get_Tsne_plot(byte_data , 50 , data_y , "Byte Unigrams")

#%%
Analysis.get_Tsne_plot(byte_data , 30 , data_y , "Byte Unigrams")

#%%
data_y = final_df.Class
asm_data = Analysis.normalize(final_df , asm_cols)
Analysis.get_Tsne_plot(asm_data.fillna(0) , 50 , data_y , "ASM Unigrams")


#%%
data_y = final_df.Class
asm_data = Analysis.normalize(final_df , asm_cols)
Analysis.get_Tsne_plot(asm_data.fillna(0) , 30 , data_y , "ASM Unigrams")


#%%
data_y = final_df.Class
whole_data = Analysis.normalize(final_df , asm_cols + byte_cols)
Analysis.get_Tsne_plot(whole_data.fillna(0) , 50 , data_y , "ASM + Bytes Unigrams")


#%%
data_y = final_df.Class
whole_data = Analysis.normalize(final_df , asm_cols + byte_cols)
Analysis.get_Tsne_plot(whole_data.fillna(0) , 30 , data_y , "ASM + Bytes Unigrams")


#%%
bytes_probs , _ = Analysis.get_probs(final_df , asm_cols , byte_cols)

Analysis.compare_dists(bytes_probs)

#%%
_ , asm_probs = Analysis.get_probs(final_df , asm_cols , byte_cols)

Analysis.compare_dists(asm_probs)


#%%
final_df.to_csv('final_df.csv' , header = True)

#%%

def collect_img_asm():
    for i , asmfile in tqdm(enumerate(os.listdir("asmFiles"))):
        filename = asmfile.split('.')[0]
        file = codecs.open("asmFiles/" + asmfile, 'rb')
        filelen = os.path.getsize("asmFiles/" + asmfile)
        width = int(filelen ** 0.5)
        rem = int(filelen / width)
        arr = array.array('B')
        arr.frombytes(file.read())
        file.close()
        reshaped = np.reshape(arr[:width * width], (width, width))
        reshaped = np.uint8(reshaped)
        os.remove("asmFiles/" + asmfile)
        imageio.imwrite('asmFiles/' + filename + '.png',reshaped)


collect_img_asm()

#%%
class ImageFeatureExtractor:
    @staticmethod
    def extract_image_features():
        asm_files_directory = 'asmFiles'  # Hard-coded ASM files directory
        csv_file_path = 'E:/Malware_Classification/imgdf_data.csv'  # Hard-coded CSV file path
        
        imagefeatures = np.zeros((3001, 800))
        asmfs = []
        imgfeatures_name = []

        for i, asmfile in tqdm(enumerate(os.listdir(asm_files_directory))):
            asmfs.append(asmfile[:-4])
            img = cv2.imread(os.path.join(asm_files_directory, asmfile))
            img_arr = img.flatten()[:800]
            imagefeatures[i, :] += img_arr

        for i in range(800):
            imgfeatures_name.append('pix' + str(i))

        imgdf = pd.DataFrame(normalize(imagefeatures, axis=0), columns=imgfeatures_name)
        imgdf['ID'] = asmfs

        imgdf.to_csv(csv_file_path, index=False)

    
    
ImageFeatureExtractor.extract_image_features()


#%%

image_data = pd.read_csv('imgdf_data.csv')
final_df = pd.read_csv('final_df.csv')

final_df = final_df.merge(image_data , on = "ID" , how = "inner").drop('Unnamed: 0' , axis = 1)

#%%
final_df_norm = Analysis.normalize(final_df , final_df.columns)

data_y = final_df.Class
final_df_norm = Analysis.normalize(final_df , final_df.columns)
Analysis.get_Tsne_plot(final_df_norm.fillna(0) , 50 , data_y , "Byte + ASM Unigrams + Pixel")

#%%
Analysis.get_Tsne_plot(final_df_norm.fillna(0) , 30 , data_y , "Byte + ASM Unigrams + Pixel")

#%%
final_df.to_csv("final_df_with_pix.csv" , header= True)

#%%
import warnings
warnings.filterwarnings("ignore")
import shutil
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pickle
from sklearn.manifold import TSNE
from sklearn import preprocessing
import pandas as pd
from multiprocessing import Process# this is used for multithreading
import multiprocessing
import codecs# this is used for file operations 
import random as r
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import log_loss
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB

from sklearn.metrics import confusion_matrix, log_loss, classification_report

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB

class NaiveBayesClassifier:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42)

    def tune_params(self, estimator, param_grid):
        grid = GridSearchCV(estimator=estimator, param_grid=param_grid, cv=5, scoring='accuracy')
        grid.fit(self.X_train, self.y_train)
        best_params = grid.best_params_
        best_score = grid.best_score_
        best_estimator = grid.best_estimator_
        test_accuracy = best_estimator.score(self.X_test, self.y_test)
        return best_params, best_score, test_accuracy , best_estimator

    def perform_tuning(self):
        gnb_params = {'var_smoothing': [1e-9, 1e-8, 1e-7]}  # Gaussian
        mnb_params = {'alpha': [0.1, 0.5, 1.0]}  # Multinomial
        bnb_params = {'alpha': [0.1, 0.5, 1.0]}  # Bernoulli

        gnb = GaussianNB()
        mnb = MultinomialNB()
        bnb = BernoulliNB()

        best_params_gnb, best_score_gnb, test_accuracy_gnb, gnb_be = self.tune_params(gnb, gnb_params)
        best_params_mnb, best_score_mnb, test_accuracy_mnb , mnb_be= self.tune_params(mnb, mnb_params)
        best_params_bnb, best_score_bnb, test_accuracy_bnb , bnb_be= self.tune_params(bnb, bnb_params)

        print("Gaussian Naive Bayes - Best Parameters:", best_params_gnb)
        print("Gaussian Naive Bayes - Best Accuracy Score:", best_score_gnb)
        print("Test Set Accuracy - Gaussian Naive Bayes:", test_accuracy_gnb)

        print("Multinomial Naive Bayes - Best Parameters:", best_params_mnb)
        print("Multinomial Naive Bayes - Best Accuracy Score:", best_score_mnb)
        print("Test Set Accuracy - Multinomial Naive Bayes:", test_accuracy_mnb)

        print("Bernoulli Naive Bayes - Best Parameters:", best_params_bnb)
        print("Bernoulli Naive Bayes - Best Accuracy Score:", best_score_bnb)
        print("Test Set Accuracy - Bernoulli Naive Bayes:", test_accuracy_bnb)

        return gnb_be , mnb_be , bnb_be

class TestMetricsMulticlass:
    def __init__(self, y_true, y_pred_proba):
        self.y_true = y_true
        self.y_pred_proba = y_pred_proba

    def compute_confusion_matrix(self):
        y_pred = self.y_pred_proba.argmax(axis=1)
        return confusion_matrix(self.y_true, y_pred)

    def compute_classification_report(self):
        y_pred = self.y_pred_proba.argmax(axis=1)
        return classification_report(self.y_true, y_pred)

    def compute_multiclass_log_loss(self):
        return log_loss(self.y_true, self.y_pred_proba)

    @staticmethod
    def plot_confusion_matrix(test_y, predict_y):

        C = confusion_matrix(test_y, predict_y)
        print("Number of misclassified points ",(len(test_y)-np.trace(C))/len(test_y)*100)
       
        A =(((C.T)/(C.sum(axis=1))).T)
        B =(C/C.sum(axis=0))
        

        labels = [1,2,3,4,5,6,7,8,9]
        cmap=sns.light_palette("green")
        # representing A in heatmap format
        print("-"*50, "Confusion matrix", "-"*50)
        plt.figure(figsize=(10,5))
        sns.heatmap(C, annot=True, cmap=cmap, fmt=".3f", xticklabels=labels, yticklabels=labels)
        plt.xlabel('Predicted Class')
        plt.ylabel('Original Class')
        plt.show()

        print("-"*50, "Precision matrix", "-"*50)
        plt.figure(figsize=(10,5))
        sns.heatmap(B, annot=True, cmap=cmap, fmt=".3f", xticklabels=labels, yticklabels=labels)
        plt.xlabel('Predicted Class')
        plt.ylabel('Original Class')
        plt.show()
        print("Sum of columns in precision matrix",B.sum(axis=0))

        # representing B in heatmap format
        print("-"*50, "Recall matrix"    , "-"*50)
        plt.figure(figsize=(10,5))
        sns.heatmap(A, annot=True, cmap=cmap, fmt=".3f", xticklabels=labels, yticklabels=labels)
        plt.xlabel('Predicted Class')
        plt.ylabel('Original Class')
        plt.show()
        print("Sum of rows in precision matrix",A.sum(axis=1))



final_df = pd.read_csv('final_df.csv').drop('Unnamed: 0' , axis = 1)
final_df_norm = Analysis.normalize(final_df , final_df.columns).drop('ID' , axis = 1)

final_df

#%%
bytes_cols = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
'0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', 
'15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', 
'20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', 
'2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', 
'36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', 
'41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', 
'4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', 
'57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', 
'62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', 
'6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', 
'78', '79', '7a', '7b', '7c', '7d', '7e', '7f', '80', '81', '82', 
'83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', 
'8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', 
'99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 
'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 
'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 
'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 
'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 
'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 
'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 
'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 
'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 
'fc', 'fd', 'fe', 'ff', '??']

X = final_df[bytes_cols]
Y = final_df['Class']

nb_classifier = NaiveBayesClassifier(X, Y)
gnb_byt , mnb_byt , bnb_byt = nb_classifier.perform_tuning()

#%%

test_metrics_multiclass = TestMetricsMulticlass(Y, gnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , gnb_byt.predict(X))


#%%
test_metrics_multiclass = TestMetricsMulticlass(Y, mnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , mnb_byt.predict(X))



#%%

test_metrics_multiclass = TestMetricsMulticlass(Y, bnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , bnb_byt.predict(X))


#%%
asm_cols = ['HEADER:', '.text:', '.Pav:', '.idata:', '.data:', '.bss:', '.rdata:', 
'.edata:', '.rsrc:', '.tls:', '.reloc:', '.BSS:', '.CODE', 'jmp', 'mov', 'retf', 
'push', 'pop', 'xor', 'retn', 'nop', 'sub', 'inc', 'dec', 'add', 'imul', 'xchg', 
'or', 'shr', 'cmp', 'call', 'shl', 'ror', 'rol', 'jnb', 'jz', 'rtn', 'lea', 'movzx', 
'.dll', 'std::', ':dword', 'edx', 'esi', 'eax', 'ebx', 'ecx', 'edi', 'ebp', 'esp', 'eip']


X = final_df[asm_cols]
Y = final_df['Class']

nb_classifier = NaiveBayesClassifier(X, Y)
gnb_byt , mnb_byt , bnb_byt = nb_classifier.perform_tuning()


#%%
test_metrics_multiclass = TestMetricsMulticlass(Y, gnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , gnb_byt.predict(X))

#%%
test_metrics_multiclass = TestMetricsMulticlass(Y, mnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , mnb_byt.predict(X))

#%%
test_metrics_multiclass = TestMetricsMulticlass(Y, bnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , bnb_byt.predict(X))

#%%
X = final_df[asm_cols + bytes_cols]
Y = final_df['Class']

nb_classifier = NaiveBayesClassifier(X, Y)
gnb_byt , mnb_byt , bnb_byt = nb_classifier.perform_tuning()

#%%
test_metrics_multiclass = TestMetricsMulticlass(Y, gnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , gnb_byt.predict(X))

#%%
test_metrics_multiclass = TestMetricsMulticlass(Y, mnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , mnb_byt.predict(X))

#%%
test_metrics_multiclass = TestMetricsMulticlass(Y, bnb_byt.predict_proba(X))


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(Y , bnb_byt.predict(X))

#%%
final_df = pd.read_csv('final_df_with_pix.csv').drop('Unnamed: 0' , axis = 1)

X = final_df.drop(['Class' , 'ID'] , axis = 1)
Y = final_df['Class']

nb_classifier = NaiveBayesClassifier(X, Y)
gnb_byt , mnb_byt , bnb_byt = nb_classifier.perform_tuning()

#%%
from tqdm import tqdm

x_trn_final, x_cv_final, y_trn_final, y_cv_final = train_test_split(X, Y, stratify = Y, test_size = 0.20)

alpha=[10,100,1000,2000]


cv_log_error_array=[]

for i in tqdm(alpha):
    x_cfl=XGBClassifier(n_estimators=i)
    x_cfl.fit(x_trn_final,y_trn_final)
    sig_clf = CalibratedClassifierCV(x_cfl, method="sigmoid")
    sig_clf.fit(x_trn_final, y_trn_final)
    predict_y = sig_clf.predict_proba(x_cv_final)
    cv_log_error_array.append(log_loss(y_cv_final, predict_y, labels=x_cfl.classes_, eps=1e-15))

for i in range(len(cv_log_error_array)):
    print ('log_loss for c = ',alpha[i],'is',cv_log_error_array[i])


best_alpha = np.argmin(cv_log_error_array)

fig, ax = plt.subplots()
ax.plot(alpha, cv_log_error_array,c='g')
for i, txt in enumerate(np.round(cv_log_error_array,3)):
    ax.annotate((alpha[i],np.round(txt,3)), (alpha[i],cv_log_error_array[i]))
plt.grid()
plt.title("Cross Validation Error for each alpha")
plt.xlabel("Alpha i's")
plt.ylabel("Error measure")
plt.show()


#%%
x_cfl=XGBClassifier(n_estimators=10,nthread=-1)
x_cfl.fit(x_trn_final,y_trn_final,verbose=True)
sig_clf = CalibratedClassifierCV(x_cfl, method="sigmoid")
sig_clf.fit(x_trn_final, y_trn_final)

predict_y = sig_clf.predict_proba(x_trn_final)
print ('For values of best alpha = ', alpha[best_alpha], "The train log loss is:",log_loss(y_trn_final, predict_y))
predict_y = sig_clf.predict_proba(x_cv_final)
print('For values of best alpha = ', alpha[best_alpha], "The cross validation log loss is:",log_loss(y_cv_final, predict_y))


#%%
test_metrics_multiclass = TestMetricsMulticlass(y_cv_final, predict_y)


class_report = test_metrics_multiclass.compute_classification_report()
print("\nClassification Report:")
print(class_report)

multiclass_logloss = test_metrics_multiclass.compute_multiclass_log_loss()
print("\nMulticlass Log Loss:", multiclass_logloss)

TestMetricsMulticlass.plot_confusion_matrix(y_cv_final, sig_clf.predict(x_cv_final))
