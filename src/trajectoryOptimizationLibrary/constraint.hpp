#pragma once
#include <functional>
#include <cmath>
#include <iterator>
#include <functional>
#include <range/v3/all.hpp>
#include "dynamic.hpp"
#include  "utilities.hpp"

namespace trajectoryOptimization::constraint{
	using namespace ranges;
	using namespace dynamics;
	using namespace trajectoryOptimization::utilities;
	using constraintFunction = std::function<std::vector<double>(const double*)>; 

	class GetToKinematicGoalSquare{
		const unsigned numberOfPoints;
		const unsigned pointDimension; 
		const unsigned kinematicDimension;
		const unsigned goalTimeIndex;
		const std::vector<double>& kinematicGoal;
		int kinematicStartIndex;
		int kinematicEndIndex;
		public:
		GetToKinematicGoalSquare(const unsigned numberOfPoints, 
														 const unsigned pointDimension,
														 const unsigned kinematicDimension,
														 const unsigned goalTimeIndex, 
														 const std::vector<double>& kinematicGoal):
			numberOfPoints(numberOfPoints),
			pointDimension(pointDimension),
			kinematicDimension(kinematicDimension),
			goalTimeIndex(goalTimeIndex),
			kinematicGoal(kinematicGoal){
			kinematicStartIndex = goalTimeIndex * pointDimension;
		}
		auto operator()(const double* trajectoryPtr) const{
			auto differentSquare = [](auto scaler1, auto scaler2)
																{return std::pow(scaler1-scaler2 ,2);};
			std::vector<double> currentKinematics;
			auto currentKinematicsStartPtr = trajectoryPtr+kinematicStartIndex;
			std::copy_n(currentKinematicsStartPtr,
									kinematicDimension,
									std::back_inserter(currentKinematics));

			auto toKinematicGoalSquareRange =
					 view::zip_with(differentSquare, kinematicGoal, currentKinematics);

			std::vector<double> toKinematicGoalSquare =
													yield_from(toKinematicGoalSquareRange);

			return toKinematicGoalSquare;
			}
	
	};

	class GetKinematicViolation{
		DynamicFunction dynamics; 
		const unsigned pointDimension;
		const unsigned positionDimension; 
		const unsigned timeIndex;
		const double dt;
		unsigned velocityDimension;
		unsigned controlDimension;
		int currentKinematicsStartIndex; 
		int nextKinematicsStartIndex; 

		public:
			GetKinematicViolation(DynamicFunction dynamics,
														const unsigned pointDimension,
														const unsigned positionDimension,
														const unsigned timeIndex,
														const double dt):
				dynamics(dynamics),
				pointDimension(pointDimension),
				positionDimension(positionDimension),
				timeIndex(timeIndex),
				dt(dt){
					// assert (kinematicDimension/2 == 0);
					velocityDimension = positionDimension;
					controlDimension = pointDimension - positionDimension- velocityDimension;
					currentKinematicsStartIndex = timeIndex*pointDimension; 
					nextKinematicsStartIndex = (timeIndex+1)*pointDimension;
				}

			std::vector<double> operator () (const double* trajectoryPointer){
				auto nowPoint = getTrajectoryPoint(trajectoryPointer,
																					 timeIndex,
																					 pointDimension);
				auto nextPoint = getTrajectoryPoint(trajectoryPointer,
																						timeIndex+1,
																						pointDimension);

				const auto& [nowPosition, nowVelocity, nowControl] = 
					getPointPositionVelocityControl(nowPoint,
																					positionDimension,
																					velocityDimension,
																					controlDimension);

				const auto& [nextPosition, nextVelocity, nextControl] = 
					getPointPositionVelocityControl(nextPoint,
																					positionDimension,
																					velocityDimension,
																					controlDimension);
				auto getViolation = [=](auto now, auto next, auto dNow, auto dNext)
						{return next - now - 0.5*dt*(dNow+dNext);}; 

				auto positionViolation = view::zip_with(getViolation,
																								nowPosition,
																								nextPosition,
																								nowVelocity,
																								nextVelocity) ;

				auto nowAcceleration = dynamics(nowPosition, nowVelocity, nowControl);
				auto nextAcceleration = dynamics(nextPosition, nextVelocity, nextControl);

				auto velocityViolation = view::zip_with(getViolation,
																								nowVelocity,
																								nextVelocity,
																								nowAcceleration,
																								nextAcceleration);

				std::vector<double> kinematicViolation = yield_from(view::concat(
																								 positionViolation,
																								 velocityViolation));
				return kinematicViolation;
			};
	};

	class StackConstriants{
		const std::vector<constraintFunction>& constraintFunctions;
		public:
			StackConstriants(const std::vector<constraintFunction>& constraintFunctions):
				constraintFunctions(constraintFunctions){};

			std::vector<double> operator()(const double* trajectoryPtr){

				std::vector<double> stackedConstriants;
				for (auto aFunction: constraintFunctions){
					auto constraints = aFunction(trajectoryPtr);
					std::copy(std::begin(constraints), std::end(constraints),
										std::back_inserter(stackedConstriants));
				}
			return stackedConstriants;
		}
	};
}

