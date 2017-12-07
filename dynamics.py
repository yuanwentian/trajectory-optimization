import numpy as np
import scipy as sp
import itertools as it
import numdifftools as nd
#this module implements dynamics and the jacobian and hessian of dyanmcis

def get_point_index(t, qdim, udim):
    # qdim, udim = self.qdim, self.udim
    point_dim = 2*qdim + udim
    start = t*point_dim
    qt_index = [start, start+qdim]
    vt_index = [qt_index[-1], qt_index[-1]+qdim]
    ut_index = [vt_index[-1], vt_index[-1]+udim]
    return qt_index, vt_index, ut_index

def get_q_v_u_from_indexes(traj, q_index, v_index, u_index):
    q = traj[q_index[0]:q_index[-1]]
    v = traj[v_index[0]:v_index[-1]]
    u = traj[u_index[0]:u_index[-1]]
    return q, v, u


def get_point_q_v_u(traj, t, qdim, udim):
    q_index, v_index, u_index = get_point_index(t, qdim, udim)
    return get_q_v_u_from_indexes(q_index, v_index, u_index)

def block_dymamics(q, v, u):
    return u


def block_dymamics_jac(q, v, u):
    jac = np.hstack([np.zeros_like(q), np.zeros_like(v), np.ones_like(u)])
    jac_2d = jac.reshape(1, -1)
    return jac_2d

class Dynamics_constriant():
    def __init__(self, prob, dynamics, dynamics_jac, t):
        #the size of the eval_g is 2*qdim, for q_dot and q_dot_dot
        #the shape of the jacobian is ( 2*qdim,  ||traj|| )
        self.prob = prob
        self.dynamics = dynamics
        self.dynamics_jac = dynamics_jac
        self.get_indexes(t)
        # self.get_constant_vel_jac_value()

        #the jacobian of the positon error is determined by postion and  velocity
        #And it is not influenced by the dynamic_jac, which is associated with acc
        #This is a constant so can be set before run time
        # self.dim_q_jac_lst = [-1, -0.5*self.prob["dt"], 1, -0.5*self.prob["dt"]]
        # self.q_jac_lst = self.dim_q_jac_lst * self.prob['qdim']

    def eval_g(self, traj):
        q0, v0, u0 = get_q_v_u_from_indexes(self.q0_i, self.v0_i, self.u0_i)
        q1, v1, u1 = get_q_v_u_from_indexes(self.q1_i, self.v1_i, self.u1_i)

        x0 = np.hstack([q0, v0])
        x1 = np.hstack([q1, v1])

        d0 = np.hstack([v0, self.dynamics(q0, v0, u0)])
        d1 = np.hstack([v1, self.dynamics(q1, v1, u1)])
        #3.2 of Kelly(2017)
        error = (x1 - x0) - 0.5*self.prob["dt"]*(d0 + d1)
        return error

    def get_indexes(self, t):
        self.q0_i, self.v0_i, self.u0_i = get_point_index(t, qdim, udim)
        self.q1_i, self.v1_i, self.u1_i = get_point_index(t+1, qdim, udim)


    def get_constant_vel_jac_value(self):
        self.dim_q_jac_lst = [-1, -0.5*self.prob["dt"], 1, -0.5*self.prob["dt"]]
        #repeat this with qdim times, one for each qdim
        self.q_jac_lst = self.dim_q_jac_lst * self.prob['qdim']


    def get_position(self):
        vel_rows, vel_cols = self.get_vel_jac_positions()
        acc_rows, acc_cols = self.get_acc_jac_positions()

        rows = np.hstack(vel_rows, acc_rows)
        cols = np.hstack(vel_cols, acc_cols)
        return rows, cols
        # dq_position = self.get_jq_position()
        # dv_position = self.get_jv_position()
        # position = dq_position + dv_position
        # return position


    def get_jq_position(self):
        pdim = 2 * self.prob["qdim"] + self.prob["udim"]
        qdim = self.prob["qdim"]
        t = self.t
        def get_dim_jac_position(t, d):
            q0_i = pdim*t + d
            q1_i = pdim*(t+1) + d
            v0_i = q0_i + qdim
            v1_i = q1_i + qdim
            return [q0_i, v0_i, q1_i, v1_i]

        q_position_lst = [get_dim_jac_position(t, d) for d in range(qdim)]
        return q_position_lst

    def get_jv_position(self):
        qdim = self.prob["qdim"]
        udim = self.prob["udim"]
        t = self.t
        q0_index, v0_index, u0_index = get_point_index(t, qdim, udim)
        q1_index, v1_index, u1_index = get_point_index(t+1, qdim, udim)
        row_v_position = list(range(q0_index[0], u1_index[-1]))#TODO: check end point
        # v_position = row_v_position*qdim
        v_position = [row_v_position for d in range(qdim)]
        return v_position

    def eval_jac_g(self, traj):
        pass

class Point_Dynamic_Error():
    def __init__(self, problem, dynamics, t):
        self.prob = problem
        self.dynamics = dynamics
        self.t = t

    def __call__(self, traj):
        #return a vector, representing the dynamic error at time i
        #the dimension of the vector is ||2 * qdim|| for q and v
        q0, v0, u0 = get_point_q_v_u(traj, self.t, prob["qdim"], prob["udim"])
        q1, v1, u1 = get_point_q_v_u(traj, self.t+1, prob["qdim"], prob["udim"])

        x0 = np.hstack([q0, v0])
        x1 = np.hstack([q1, v1])

        # the deviavie respect to [q, v], not including u: x_dot = f(x, u)
        #TODO: each point is evaluted twice; this can be improved
        d0 = np.hstack([v0, self.dynamics(q0, v0, u0)])
        d1 = np.hstack([v1, self.dynamics(q1, v1, u1)])
        error = (x1 - x0) - 0.5*self.prob["dt"]*(d0 + d1) #3.2 of Kelly(2017)
        return error


class Point_Dynamic_Jacobian():
    def __init__(self, problem, dynamics_jac, t):
        self.t = t
        self.prob = problem
        # dynamics_jac evaluats the jacobian of accelation = f(q, v, u)
        self.dynamics_jac = dynamics_jac
        #the jacobian of the positon error is determined by postion and  velocity
        #And it is not influenced by the dynamic_jac, which is associated with acc
        #This is a constant so can be set before run time
        self.dim_q_jac_lst = [-1, -0.5*self.prob["dt"], 1, -0.5*self.prob["dt"]]
        self.q_jac_lst = self.dim_q_jac_lst * self.prob['qdim']

        #the position of non-zero jacobian with shape(2*qdim, ||traj||)
        self.position = self.get_position()


    def get_position(self):
        dq_position = self.get_jq_position()
        dv_position = self.get_jv_position()
        position = dq_position + dv_position
        return position


    def get_jq_position(self):
        pdim = 2 * self.prob["qdim"] + self.prob["udim"]
        qdim = self.prob["qdim"]
        t = self.t
        def get_dim_jac_position(t, d):
            q0_i = pdim*t + d
            q1_i = pdim*(t+1) + d
            v0_i = q0_i + qdim
            v1_i = q1_i + qdim
            return [q0_i, v0_i, q1_i, v1_i]

        q_position_lst = [get_dim_jac_position(t, d) for d in range(qdim)]
        return q_position_lst

    def get_jv_position(self):
        qdim = self.prob["qdim"]
        udim = self.prob["udim"]
        t = self.t
        q0_index, v0_index, u0_index = get_point_index(t, qdim, udim)
        q1_index, v1_index, u1_index = get_point_index(t+1, qdim, udim)
        row_v_position = list(range(q0_index[0], u1_index[-1]))#TODO: check end point
        # v_position = row_v_position*qdim
        v_position = [row_v_position for d in range(qdim)]
        return v_position


    def value(self, traj):
        #TODO: check this function !!
        #values of non-zero jacobian; the full jacobian is (2*qdim, ||traj||)
        #the jacobian of the positon error is determined by postion and  velocity
        #And it is not influenced by the dynamic_jac, which is associated with acc
        # q_jac_lst = [-1, -0.5*self.prob["dt"], 1, -0.5*self.prob["dt"]] * self.qdim
        # postion derivative
        t = self.t
        dt = self.prob["dt"]
        qdim = self.prob["qdim"]
        udim = self.prob["udim"]

        q0, v0, u0 = get_point_q_v_u(traj, t, qdim, udim)
        q1, v1, u1 = get_point_q_v_u(traj, t+1, qdim, udim)

        a0_jac = self.dynamics_jac(q0, v0, u0)
        a1_jac = self.dynamics_jac(q1, v1, u1)

        dq0 = -0.5*dt*a0_jac[:,0:qdim]
        dv0 = -1 - 0.5*dt*a0_jac[:, qdim:2*qdim]
        du0 = -0.5*dt*a0_jac[:, 2*qdim:2*qdim+udim]

        dq1 = -0.5*dt*a1_jac[:,0:qdim]
        dv1 = 1 - 0.5*dt*a1_jac[:, qdim:2*qdim]
        du1 = -0.5*dt*a1_jac[:, 2*qdim:2*qdim+udim]

        v_jac = np.concatenate([dq0, dv0, du0, dq1, dv1, du1], axis=1)
        v_jac_flat = v_jac.flatten()

        point_jac_flat = np.hstack([self.q_jac_lst, v_jac_flat])
        return point_jac_flat


    def __call__(self, traj, flag):
        if flag:
            return self.position
        return self.value(traj)


def traj_dynamic_error_function_factory(prob, dynamics):
    #number of trajectory point
    n = prob["n"]
    #there is no dynamic constriant for the last point
    func_lst = [Point_Dynamic_Error(prob, dynamics, t) for t in range(n-1)]
    return func_lst


def traj_dynamic_jacobian_function_factory(prob, dynamics_jac):
    n = prob["n"]
    #there is no dynamic constriant for the last point
    func_lst =[Point_Dynamic_Jacobian(prob, dynamics_jac, t)
               for t in range(n-1)]
    return func_lst


def traj_dynamic_hessian_function_factory(prob, dynamics_hessian):
    n = prob["n"]
    #there is no dynamic constriant for the last point
    func_lst =[Point_Dynamic_Jacobian(prob, dynamics_hessian, t)
               for t in range(n-1)]



if __name__=="__main__":
    prob = {}
    prob["n"] =  2 # number of trajectory point
    prob["dt"] = 1.0/prob["n"]
    # prob["start"] = (0, 0)
    # prob["end"] = (1, 1)
    prob["qdim"] = 1
    prob["udim"] = 1


    start = (0, 0)
    end = (0, 0)
    n = prob['n']
    q_arr = np.linspace(start[0], end[0], n)
    v_arr = np.linspace(start[1], end[1], n)
    # q_arr = np.zeros(n)
    # v_arr = np.zeros(n)
    u_arr = np.ones_like(q_arr, dtype=float)*-10
    X_init = np.vstack([q_arr, v_arr, u_arr]).flatten("F")

    dynamic_g_lst = traj_dynamic_error_function_factory(prob, block_dymamics)
    dynamic_g_jac_lst = traj_dynamic_jacobian_function_factory(prob, block_dymamics_jac)

    goal = (0.05, 0.05)
    start_g = Point_q_v_error(prob, goal, 0)
    start_g_jac = Point_q_v_jacobian(prob, start, 0)


    end_g = Point_q_v_error(prob, end, n-1)
    end_g_jac = Point_q_v_jacobian(prob, end, n-1)

    # g_lst = dynamic_g_lst+ [start_g]
    # g_jac_lst = dynamic_g_jac_lst+[start_g_jac]

    # g_lst = dynamic_g_lst+ [end_g]
    # g_jac_lst = dynamic_g_jac_lst+[end_g_jac]

    # g_lst = [start_g, end_g]
    # g_jac_lst = [start_g_jac, end_g_jac]

    # g_lst = [end_g]
    # g_jac_lst = [end_g_jac]

    g_lst = [start_g]
    g_jac_lst = [start_g_jac]

    ipopt_g = Ipopt_Constriants(g_lst)
    ipopt_g_jac = Ipopt_Constriants_Jacobian(g_jac_lst)

    g_error = ipopt_g(X_init)
    mask = ipopt_g_jac(X_init, True)
    jac = ipopt_g_jac(X_init, False)
    #

    value = ipopt_g_jac(X_init, False)
    pos = ipopt_g_jac(X_init, True)


    jac_pos = ipopt_g_jac(X_init, True)
    jac_value = ipopt_g_jac(X_init, False)

    #set the optimization problem
    nvar = X_init.size
    x_L = np.ones(nvar)*-10
    x_U = np.ones(nvar)*10

    ncon = len(ipopt_g(X_init))

    g_L = np.ones(ncon)*-0.0001
    g_U = np.ones(ncon)*0.0001

    nnzj = jac_pos[0].size

    eval_grad_f = Control_square_cost(prob)

    # eval_grad_f(X_init)
    eval_g = ipopt_g
    eval_jac_g = ipopt_g_jac

    nlp = ip.create(nvar, x_L, x_U, ncon, g_L, g_U, nnzj, 0, eval_f, eval_grad_f, eval_g, eval_jac_g)

    x, zl, zu, constraint_multipliers, obj, status = nlp.solve(X_init)
    nlp.close()

    print (x)

