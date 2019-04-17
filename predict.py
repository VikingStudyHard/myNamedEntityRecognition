import yaml
import pickle
import tensorflow as tf
from load_data import load_vocs, init_data
from model import SequenceLabelingModel
from test_data_prepare import writetxt


# 加载配置文件
with open('./config.yml', 'rb') as file_config:
    # config = yaml as yaml.load(file_config)
    config = yaml.load(file_config)
feature_names = config['model_params']['feature_names']

# 初始化embedding shape, dropouts, 预训练的embedding也在这里初始化)
feature_weight_shape_dict, feature_weight_dropout_dict, feature_init_weight_dict = dict(), dict(), dict()
for feature_name in feature_names:
    feature_weight_shape_dict[feature_name] = \
        config['model_params']['embed_params'][feature_name]['shape']
    feature_weight_dropout_dict[feature_name] = \
        config['model_params']['embed_params'][feature_name]['dropout_rate']
    path_pre_train = config['model_params']['embed_params'][feature_name]['path']
    if path_pre_train:
        with open(path_pre_train, 'rb') as file_r:
            feature_init_weight_dict[feature_name] = pickle.load(file_r)

# 加载vocs
path_vocs = []
for feature_name in feature_names:
    path_vocs.append(config['data_params']['voc_params'][feature_name]['path'])
path_vocs.append(config['data_params']['voc_params']['label']['path'])
vocs = load_vocs(path_vocs)
print(vocs[-1])
print(len(vocs))
# 加载模型
model = SequenceLabelingModel(
    sequence_length=config['model_params']['sequence_length'],
    nb_classes=config['model_params']['nb_classes'],
    nb_hidden=config['model_params']['bilstm_params']['num_units'],
    feature_weight_shape_dict=feature_weight_shape_dict,
    feature_init_weight_dict=feature_init_weight_dict,
    feature_weight_dropout_dict=feature_weight_dropout_dict,
    dropout_rate=config['model_params']['dropout_rate'],
    nb_epoch=config['model_params']['nb_epoch'], feature_names=feature_names,
    batch_size=config['model_params']['batch_size'],
    train_max_patience=config['model_params']['max_patience'],
    use_crf=config['model_params']['use_crf'],
    l2_rate=config['model_params']['l2_rate'],
    rnn_unit=config['model_params']['rnn_unit'],
    learning_rate=config['model_params']['learning_rate'],
    path_model=config['model_params']['path_model'])


def predict(string):
    choiceAction = []
    choiceTarget = []
    choiceData = []
    lab = writetxt(string)
    # 加载数据
    if len(lab[0]) == 0:
        return 'ok;None'
    sep_str = config['data_params']['sep']
    assert sep_str in ['table', 'space']
    sep = '\t' if sep_str == 'table' else ' '
    data_dict = init_data(
        path=config['data_params']['path_test'], feature_names=feature_names, sep=sep,
        vocs=vocs, max_len=config['model_params']['sequence_length'], model='test')

    saver = tf.train.Saver()
    saver.restore(model.sess, config['model_params']['path_model'])

    seq = model.predict(data_dict)
    print(seq)
    for i in range(len(seq)):
        delOne = ''
        if (6 in seq[i] or 11 in seq[i] or 7 in seq[i] or 10 in seq[i]):
            tem = ""
            for j in range(len(seq[i])):
                if seq[i][j] == 6 or seq[i][j] == 7:
                    tem += lab[i][j]
                if seq[i][j] == 10:
                    choiceAction.append(lab[i][j])
            if len(tem) > 0:
                choiceAction.append(tem)
    ch = '***'.join(choiceAction)
    finalAction = '' + ch
    if finalAction == '':
        finalAction = '0'
    for i in range(len(seq)):
        if (4 in seq[i] or 3 in seq[i] or 5 in seq[i] or 13 in seq[i]):
            tem = ""
            for j in range(len(seq[i])):
                if seq[i][j] == 4 or seq[i][j] == 3 or seq[i][j] == 5:
                    tem += lab[i][j]
                if seq[i][j] == 13:
                    choiceTarget.append(lab[i][j])
            if len(tem) > 0:
                choiceTarget.append(tem)
    ch = '***'.join(choiceTarget)
    finalTarget = '' + ch
    if finalTarget == '':
        finalTarget = '0'
    for i in range(len(seq)):
        if (8 in seq[i] or 2 in seq[i] or 9 in seq[i] or 12 in seq[i]):
            tem = ""
            for j in range(len(seq[i])):
                if seq[i][j] == 8 or seq[i][j] == 2 or seq[i][j] == 9:
                    tem += lab[i][j]
                if seq[i][j] == 12:
                    choiceData.append(lab[i][j])
            if len(tem) > 0:
                choiceData.append(tem)
    ch = '***'.join(choiceData)
    finalData = '' + ch
    if finalData == '':
        finalData = '0'
    return finalAction, finalTarget, finalData


#resultp, resultt, da = predict('在变更后MDS名称中填写MBRASSY-FRSIDERH')
#print(resultp, resultt, da)
