/* $Id: pow_op.hpp 2910 2013-10-07 13:27:58Z bradbell $ */
# ifndef CPPAD_POW_OP_INCLUDED
# define CPPAD_POW_OP_INCLUDED

/* --------------------------------------------------------------------------
CppAD: C++ Algorithmic Differentiation: Copyright (C) 2003-13 Bradley M. Bell

CppAD is distributed under multiple licenses. This distribution is under
the terms of the 
                    Eclipse Public License Version 1.0.

A copy of this license is included in the COPYING file of this distribution.
Please visit http://www.coin-or.org/CppAD/ for information on other licenses.
-------------------------------------------------------------------------- */

namespace CppAD { // BEGIN_CPPAD_NAMESPACE
/*!
\defgroup pow_op_hpp pow_op.hpp
\{
\file pow_op.hpp
Forward and reverse mode calculations for z = pow(x, y).
*/

// --------------------------- Powvv -----------------------------------------
/*!
Compute forward mode Taylor coefficients for result of op = PowvvOp.

In the documentation below,
this operations is for the case where both x and y are variables
and the argument \a parameter is not used.

\copydetails forward_pow_op
*/

template <class Base>
inline void forward_powvv_op(
	size_t        q           , 
	size_t        p           , 
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	Base*         taylor      )
{
	// convert from final result to first result
	i_z -= 2; // 2 = NumRes(PowvvOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowvvOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowvvOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[0]) < i_z );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[1]) < i_z );
	CPPAD_ASSERT_UNKNOWN( p < nc_taylor );
	CPPAD_ASSERT_UNKNOWN( q <= p );

	// z_0 = log(x)
	forward_log_op(q, p, i_z, arg[0], nc_taylor, taylor);

	// z_1 = z_0 * y
	addr_t adr[2];
	adr[0] = i_z;
	adr[1] = arg[1];
	forward_mulvv_op(q, p, i_z+1, adr, parameter, nc_taylor, taylor);

	// z_2 = exp(z_1)
	// final result for zero order case is exactly the same as for Base
	if( q == 0 )
	{	// Taylor coefficients corresponding to arguments and result
		Base* x   = taylor + arg[0]  * nc_taylor;
		Base* y   = taylor + arg[1]  * nc_taylor;
		Base* z_2 = taylor + (i_z+2) * nc_taylor;

		z_2[0] = pow(x[0], y[0]);
		q++;
	}
	if( q <= p )
		forward_exp_op(q, p, i_z+2, i_z+1, nc_taylor, taylor);
}

/*!
Compute zero order forward mode Taylor coefficients for result of op = PowvvOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where both x and y are variables
and the argument \a parameter is not used.

\copydetails forward_pow_op_0
*/

template <class Base>
inline void forward_powvv_op_0(
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	Base*         taylor      )
{
	// convert from final result to first result
	i_z -= 2; // NumRes(PowvvOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowvvOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowvvOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[0]) < i_z );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[1]) < i_z );

	// Taylor coefficients corresponding to arguments and result
	Base* x   = taylor + arg[0] * nc_taylor;
	Base* y   = taylor + arg[1] * nc_taylor;
	Base* z_0 = taylor + i_z    * nc_taylor;
	Base* z_1 = z_0    +          nc_taylor;
	Base* z_2 = z_1    +          nc_taylor;

	z_0[0] = log( x[0] );
	z_1[0] = z_0[0] * y[0];
	z_2[0] = pow(x[0], y[0]);

}

/*!
Compute reverse mode partial derivatives for result of op = PowvvOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where both x and y are variables
and the argument \a parameter is not used.

\copydetails reverse_pow_op
*/

template <class Base>
inline void reverse_powvv_op(
	size_t        d           , 
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	const Base*   taylor      ,
	size_t        nc_partial  ,
	Base*         partial     )
{
	// convert from final result to first result
	i_z -= 2; // NumRes(PowvvOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowvvOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowvvOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[0]) < i_z );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[1]) < i_z );
	CPPAD_ASSERT_UNKNOWN( d < nc_taylor );
	CPPAD_ASSERT_UNKNOWN( d < nc_partial );

	// z_2 = exp(z_1)
	reverse_exp_op(
		d, i_z+2, i_z+1, nc_taylor, taylor, nc_partial, partial
	);

	// z_1 = z_0 * y
	addr_t adr[2];
	adr[0] = i_z;
	adr[1] = arg[1];
	reverse_mulvv_op(
	d, i_z+1, adr, parameter, nc_taylor, taylor, nc_partial, partial
	);

	// z_0 = log(x)
	reverse_log_op(
		d, i_z, arg[0], nc_taylor, taylor, nc_partial, partial
	);
}

// --------------------------- Powpv -----------------------------------------
/*!
Compute forward mode Taylor coefficients for result of op = PowpvOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where x is a parameter and y is a variable.

\copydetails forward_pow_op
*/

template <class Base>
inline void forward_powpv_op(
	size_t        q           , 
	size_t        p           , 
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	Base*         taylor      )
{
	// convert from final result to first result
	i_z -= 2; // 2 = NumRes(PowpvOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowpvOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowpvOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[1]) < i_z );
	CPPAD_ASSERT_UNKNOWN( p < nc_taylor );
	CPPAD_ASSERT_UNKNOWN( q <= p );

	// Taylor coefficients corresponding to arguments and result
	Base* z_0 = taylor + i_z    * nc_taylor;

	// z_0 = log(x)
	Base x    = parameter[ arg[0] ];
	size_t d;
	for(d = q; d <= p; d++)
	{	if( d == 0 )
			z_0[d] = log(x);
		else	z_0[d] = Base(0);
	}

	// z_1 = z_0 * y
	addr_t adr[2];
	adr[0] = i_z * nc_taylor; // offset of z_0 in taylor; i.e., log(x)
	adr[1] = arg[1];          // variable index of y in taylor

	// use taylor both for parameter and variable values (trick)
	forward_mulpv_op(q, p, i_z+1, adr, taylor, nc_taylor, taylor);

	// z_2 = exp(z_1)
	// zero order case exactly same as Base type operation
	if( q == 0 )
	{	Base* y   = taylor + arg[1]  * nc_taylor;
		Base* z_2 = taylor + (i_z+2) * nc_taylor;
		z_2[0] = pow(x, y[0]);
		q++;
	}
	if( q <= p )
		forward_exp_op(q, p, i_z+2, i_z+1, nc_taylor, taylor);
}
/*!
Compute zero order forward mode Taylor coefficient for result of op = PowpvOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where x is a parameter and y is a variable.

\copydetails forward_pow_op_0
*/

template <class Base>
inline void forward_powpv_op_0(
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	Base*         taylor      )
{
	// convert from final result to first result
	i_z -= 2; // NumRes(PowpvOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowpvOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowpvOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[1]) < i_z );

	// Paraemter value
	Base x = parameter[ arg[0] ];

	// Taylor coefficients corresponding to arguments and result
	Base* y   = taylor + arg[1] * nc_taylor;
	Base* z_0 = taylor + i_z    * nc_taylor;
	Base* z_1 = z_0    +          nc_taylor;
	Base* z_2 = z_1    +          nc_taylor;

	// z_0 = log(x)
	z_0[0] = log(x);

	// z_1 = z_0 * y
	z_1[0] = z_0[0] * y[0];

	// z_2 = exp(z_1)
	// zero order case exactly same as Base type operation
	z_2[0] = pow(x, y[0]);
}

/*!
Compute reverse mode partial derivative for result of op = PowpvOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where x is a parameter and y is a variable.

\copydetails reverse_pow_op
*/

template <class Base>
inline void reverse_powpv_op(
	size_t        d           , 
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	const Base*   taylor      ,
	size_t        nc_partial  ,
	Base*         partial     )
{
	// convert from final result to first result
	i_z -= 2; // NumRes(PowpvOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowvvOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowvvOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[1]) < i_z );
	CPPAD_ASSERT_UNKNOWN( d < nc_taylor );
	CPPAD_ASSERT_UNKNOWN( d < nc_partial );

	// z_2 = exp(z_1)
	reverse_exp_op(
		d, i_z+2, i_z+1, nc_taylor, taylor, nc_partial, partial
	);

	// z_1 = z_0 * y
	addr_t adr[2];
	adr[0] = i_z * nc_taylor; // offset of z_0[0] in taylor 
	adr[1] = arg[1];          // index of y in taylor and partial
	// use taylor both for parameter and variable values
	reverse_mulpv_op(
		d, i_z+1, adr, taylor, nc_taylor, taylor, nc_partial, partial
	);

	// z_0 = log(x)
	// x is a parameter
}

// --------------------------- Powvp -----------------------------------------
/*!
Compute forward mode Taylor coefficients for result of op = PowvvOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where x is a variable and y is a parameter.

\copydetails forward_pow_op
*/

template <class Base>
inline void forward_powvp_op(
	size_t        q           , 
	size_t        p           , 
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	Base*         taylor      )
{
	// convert from final result to first result
	i_z -= 2; // 2 = NumRes(PowvpOp) - 1

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowvpOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowvpOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[0]) < i_z );
	CPPAD_ASSERT_UNKNOWN( p < nc_taylor );
	CPPAD_ASSERT_UNKNOWN( q <= p );

	// z_0 = log(x)
	forward_log_op(q, p, i_z, arg[0], nc_taylor, taylor);

	// z_1 = y * z_0
	addr_t adr[2];
	adr[0] = arg[1];
	adr[1] = i_z;
	forward_mulpv_op(q, p, i_z+1, adr, parameter, nc_taylor, taylor);

	// z_2 = exp(z_1)
	// zero order case exactly same as Base type operation
	if( q == 0 )
	{	Base* z_2 = taylor + (i_z+2) * nc_taylor;
		Base* x   = taylor + arg[0] * nc_taylor;
		Base  y   = parameter[ arg[1] ];
		z_2[0]  = pow(x[0], y);
		q++;
	}
	if( q <= p )
		forward_exp_op(q, p, i_z+2, i_z+1, nc_taylor, taylor);
}

/*!
Compute zero order forward mode Taylor coefficients for result of op = PowvvOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where x is a variable and y is a parameter.

\copydetails forward_pow_op_0
*/

template <class Base>
inline void forward_powvp_op_0(
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	Base*         taylor      )
{
	// convert from final result to first result
	i_z -= 2; // NumRes(PowvpOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowvpOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowvpOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[0]) < i_z );

	// Paraemter value
	Base y = parameter[ arg[1] ];

	// Taylor coefficients corresponding to arguments and result
	Base* x   = taylor + arg[0] * nc_taylor;
	Base* z_0 = taylor + i_z    * nc_taylor;
	Base* z_1 = z_0    +          nc_taylor;
	Base* z_2 = z_1    +          nc_taylor;

	// z_0 = log(x)
	z_0[0] = log(x[0]);

	// z_1 = z_0 * y
	z_1[0] = z_0[0] * y;

	// z_2 = exp(z_1)
	// zero order case exactly same as Base type operation
	z_2[0] = pow(x[0], y);
}

/*!
Compute reverse mode partial derivative for result of op = PowvpOp.

The C++ source code corresponding to this operation is
\verbatim
	z = pow(x, y)
\endverbatim
In the documentation below,
this operations is for the case where x is a variable and y is a parameter.

\copydetails reverse_pow_op
*/

template <class Base>
inline void reverse_powvp_op(
	size_t        d           , 
	size_t        i_z         ,
	const addr_t* arg         ,
	const Base*   parameter   ,
	size_t        nc_taylor   ,
	const Base*   taylor      ,
	size_t        nc_partial  ,
	Base*         partial     )
{
	// convert from final result to first result
	i_z -= 2; // NumRes(PowvpOp) - 1;

	// check assumptions
	CPPAD_ASSERT_UNKNOWN( NumArg(PowvpOp) == 2 );
	CPPAD_ASSERT_UNKNOWN( NumRes(PowvpOp) == 3 );
	CPPAD_ASSERT_UNKNOWN( size_t(arg[0]) < i_z );
	CPPAD_ASSERT_UNKNOWN( d < nc_taylor );
	CPPAD_ASSERT_UNKNOWN( d < nc_partial );

	// z_2 = exp(z_1)
	reverse_exp_op(
		d, i_z+2, i_z+1, nc_taylor, taylor, nc_partial, partial
	);

	// z_1 = y * z_0
	addr_t adr[2];
	adr[0] = arg[1];
	adr[1] = i_z;
	reverse_mulpv_op(
	d, i_z+1, adr, parameter, nc_taylor, taylor, nc_partial, partial
	);

	// z_0 = log(x)
	reverse_log_op(
		d, i_z, arg[0], nc_taylor, taylor, nc_partial, partial
	);
}

/*! \} */
} // END_CPPAD_NAMESPACE
# endif
