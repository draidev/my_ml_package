from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score, precision_score, recall_score
import seaborn as sns

def get_binary_matrix(y_val, y_pred):
    accuracy = accuracy_score(y_val, y_pred)
    recall = recall_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred)

    print('accuracy :', accuracy)
    print('recall :', recall)
    print('precision :', precision)
    print('f1-score :', f1)

    return accuracy, recall, precision, f1


def get_multiclass_matrix(y_val, y_pred):
    print("<< confusion matrix >>")
    print("="*30)
    cm = confusion_matrix(y_val, y_pred)
    print(cm)
    sns.heatmap(cm, annot=True, cmap='Blues')


    print("\n\n<< classification report >>")
    print("="*60)
    print(classification_report(y_val, y_pred))

    acc = accuracy_score(y_val, y_pred) 
    recall = recall_score(y_val, y_pred, average='macro')
    precision = precision_score(y_val, y_pred, average='macro')
    f1 = f1_score(y_val, y_pred, average='macro')

    return acc, recall, precision, f1
