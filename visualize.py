import argparse
import os
import torch
import numpy as np
from attrdict import AttrDict
import matplotlib.pyplot as plt
from matplotlib import animation

from sgan.data.loader import data_loader
from sgan.models import TrajectoryGenerator
from sgan.utils import relative_to_abs, get_dset_path

parser = argparse.ArgumentParser()
parser.add_argument('--model_path', type=str)
parser.add_argument('--num_samples', default=20, type=int)
parser.add_argument('--dset_type', default='test', type=str)

gorund_truth_points_total, predicted_points_total = [], []
xdata0, ydata0 = [], []
xdata1, ydata1 = [], []

xdata2, ydata2 = [], []

xdata3, ydata3 = [], []

xdata4, ydata4 = [], []

xdata5, ydata5 = [], []

xdata6, ydata6 = [], []
xdata7, ydata7 = [], []

x11, y11, x12, y12, x13, y13, x14, y14 = [], [], [], [], [], [], [], []
x01, y01, x02, y02, x03, y03, x04, y04 = [], [], [], [], [], [], [], []

aa, bb = [], []
num_t = 0
fig, ax = plt.subplots()

ln11, = ax.plot([], [], 'b--')
ln12, = ax.plot([], [], 'g--')

ln21, = ax.plot([], [], 'r--')
ln22, = ax.plot([], [], 'c--')

ln31, = ax.plot([], [], 'b:')
ln32, = ax.plot([], [], 'g:')

ln41, = ax.plot([], [], 'r:')
ln42, = ax.plot([], [], 'c:')


def init():
    ax.set_xlim(-10, 15)
    ax.set_ylim(-10, 15)


def gen_dot():
    for i in range(0, len(x01)):
        newdot = [x01[i], y01[i]]
        yield newdot


def update_dot(newd):
    global num_t
    if num_t < len(x01):
        xdata0.append(newd[0])  # x01
        ydata0.append(newd[1])  # y01

        xdata1.append(x02[num_t])
        ydata1.append(y02[num_t])

        xdata2.append(x03[num_t])
        ydata2.append(y03[num_t])

        xdata3.append(x04[num_t])
        ydata3.append(y04[num_t])

        xdata4.append(x11[num_t])
        ydata4.append(y11[num_t])

        xdata5.append(x12[num_t])
        ydata5.append(y12[num_t])

        xdata6.append(x13[num_t])
        ydata6.append(y13[num_t])

        xdata7.append(x14[num_t])
        ydata7.append(y14[num_t])

        num_t = num_t + 1

        ln11.set_data(xdata0, ydata0)
        ln12.set_data(xdata1, ydata1)

        ln21.set_data(xdata2, ydata2)
        ln22.set_data(xdata3, ydata3)

        ln31.set_data(xdata4, ydata4)
        ln32.set_data(xdata5, ydata5)

        ln41.set_data(xdata6, ydata6)
        ln42.set_data(xdata7, ydata7)

        return ln11, ln12, ln21, ln22, ln31, ln32, ln41, ln42


def plot():
    global x01, x02, x03, x04, y01, y02, y03, y04, x11, x12, x13, x14, y11, y12, y13, y14

    x01 = gorund_truth_points_total[0][:, 0]
    y01 = gorund_truth_points_total[0][:, 1]
    x02 = gorund_truth_points_total[1][:, 0]
    y02 = gorund_truth_points_total[1][:, 1]
    x03 = gorund_truth_points_total[2][:, 0]
    y03 = gorund_truth_points_total[2][:, 1]
    x04 = gorund_truth_points_total[3][:, 0]
    y04 = gorund_truth_points_total[3][:, 1]
    x11 = predicted_points_total[0][:, 0]
    y11 = predicted_points_total[0][:, 1]
    x12 = predicted_points_total[1][:, 0]
    y12 = predicted_points_total[1][:, 1]
    x13 = predicted_points_total[2][:, 0]
    y13 = predicted_points_total[2][:, 1]
    x14 = predicted_points_total[3][:, 0]
    y14 = predicted_points_total[3][:, 1]

    ani = animation.FuncAnimation(fig, update_dot, frames=gen_dot, interval=500, init_func=init)
    ani.save('./animation.mp4')
    plt.savefig('./trajectory_prediction.png')
    # you can make the interval bigger to see more clearly ie. interval=500
    plt.show()
    plt.close()


def get_generator(checkpoint):
    args = AttrDict(checkpoint['args'])
    generator = TrajectoryGenerator(
        obs_len=args.obs_len,
        pred_len=args.pred_len,
        embedding_dim=args.embedding_dim,
        encoder_h_dim=args.encoder_h_dim_g,
        decoder_h_dim=args.decoder_h_dim_g,
        mlp_dim=args.mlp_dim,
        num_layers=args.num_layers,
        noise_dim=args.noise_dim,
        noise_type=args.noise_type,
        noise_mix_type=args.noise_mix_type,
        pooling_type=args.pooling_type,
        pool_every_timestep=args.pool_every_timestep,
        dropout=args.dropout,
        bottleneck_dim=args.bottleneck_dim,
        neighborhood_size=args.neighborhood_size,
        grid_size=args.grid_size,
        batch_norm=args.batch_norm)
    generator.load_state_dict(checkpoint['g_state'])
    generator.cuda()
    generator.train()
    return generator


def evaluate(loader, generator):
    with torch.no_grad():
        for batch in loader:
            batch = [tensor.cuda() for tensor in batch]
            (obs_traj, pred_traj_gt, obs_traj_rel, pred_traj_gt_rel,
             non_linear_ped, loss_mask, seq_start_end) = batch

            for _ in range(1):  # num_samples
                pred_traj_fake_rel = generator(
                    obs_traj, obs_traj_rel, seq_start_end
                )
                pred_traj_fake = relative_to_abs(
                    pred_traj_fake_rel, obs_traj[-1]
                )
                gt = pred_traj_gt[:, 3, :].data
                input_a = obs_traj[:, 3, :].data
                out_a = pred_traj_fake[:, 3, :].data
                ground_truth_point = np.concatenate((input_a.cpu(), gt.cpu()), axis=0) # ground truth
                predicted_point = np.concatenate((input_a.cpu(), out_a.cpu()), axis=0) # predicted value
                global x0, y0, x1, y1, gorund_truth_points_total, predicted_points_total
                gorund_truth_points_total.append(ground_truth_point)
                predicted_points_total.append(predicted_point)


def main(args):
    if os.path.isdir(args.model_path):
        filenames = os.listdir(args.model_path)
        filenames.sort()
        paths = [
            os.path.join(args.model_path, file_) for file_ in filenames
        ]
    else:
        paths = [args.model_path]

    for path in paths:
        checkpoint = torch.load(path)
        generator = get_generator(checkpoint)
        _args = AttrDict(checkpoint['args'])
        path = get_dset_path(_args.dataset_name, args.dset_type)
        _, loader = data_loader(_args, path)
        evaluate(loader, generator)
        plot()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
