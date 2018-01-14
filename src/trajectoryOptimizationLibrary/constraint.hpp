/*
 * =====================================================================================
 *
 *       Filename:  constraint.hpp
 *
 *    Description:  constraints for trajectory optimization
 *
 *        Version:  1.0
 *        Created:  12/24/2017 05:01:27 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Tao Gao 
 *   Organization:  UCLA
 *
 * =====================================================================================
 */
#pragma once
#include <functional>
#include <cmath>
#include <range/v3/all.hpp>
#include  "utilities.hpp"

namespace traj_opt::constraint{
	template <unsigned NQ, unsigned NV, unsigned NU>
	using Dynamic_Func = std::function<Array<NQ+NV>(Array<NQ>, Array<NV>, Array<NU>)>;
	template<unsigned P>
	class Goal_Constraint{
			const Array<P>& goal;
			const int t; 
			int start; 
			int end;
		public:
			Goal_Constraint(const Array<P>& goal, const int t): goal(goal), t(t){
				start = t*P;
				end = start + P;
			}

			const Array<P> operator()(const double* x) const {
				Array<P> diff;
				auto goal_start = std::begin(goal);
				std::transform(x+start,
											 x+end,
											 goal_start,
											 std::begin(diff),
											 [](auto v1, auto v2){ return std::pow(v1-v2, 2);});
				return diff;
			};
	};

	template <unsigned NQ, unsigned NV, unsigned NU>
	class Point_Dynamic_Constraint{
			Dynamic_Func<NQ, NV, NU> dynamics;
			const int t;
			const double dt;
		public:
			Point_Dynamic_Constraint(Dynamic_Func<NQ, NV, NU> dynamics,
															 const int t, const double dt):
															 dynamics(dynamics), t(t), dt(dt){
				}

			const Array<NQ+NV> operator()(const double* x) const{
				auto const & [q0_arr, v0_arr, u0_arr] = get_q_v_u<NQ, NV, NU>(x, t);
				auto const & [q1_arr, v1_arr, u1_arr] = get_q_v_u<NQ, NV, NU>(x, t+1);

				auto qv0_rng = ranges::view::concat(q0_arr, v0_arr);
				auto qv1_rng = ranges::view::concat(q1_arr, v1_arr);

				auto d0_rng = ranges::view::concat(v0_arr, dynamics(q0_arr, v0_arr, u0_arr));
				auto d1_rng = ranges::view::concat(v1_arr, dynamics(q1_arr, v1_arr, u1_arr));

				auto grad_func = [=](auto qv0, auto qv1, auto d0, auto d1){
					return qv1 - qv0 - 0.5*dt*(d0+d1);
				};

				auto error_rng = ranges::view::zip_with(grad_func, qv0_rng, qv1_rng,
																						d0_rng, d1_rng);  
				std::vector<double> error_vec = ranges::yield_from(error_rng);
				Array<NQ+NV> error;
				std::copy_n(error_vec.begin(), NQ+NV, std::begin(error));
				return error;
			};
	};
  //
	// class Traj_Dynamic_Constriant{
	// 	public:
	// 		Traj_Dynamic_Constriant(const int n, const int pd, Point_Func point_func):
	// 	n(n), pd(pd), point_func(point_func){};
	// 		//traj is a 2d array, row_num = n; col_num = pd
	// 		const Point operator () (const Traj& traj) {
	// 			Point g;   
	// 			for (int i=0; i<n-1;i++){
	// 				Point p0 = traj.row(i);
	// 				Point p1 = traj.row(i+1);
	// 				Point error = point_func(p0, p1);
	// 				g << error;
	// 			}
	// 			return g;
	// 		};
  //
	// 	private:
	// 		const int n;
	// 		const int pd;
	// 		Point_Func point_func;
	// };
}