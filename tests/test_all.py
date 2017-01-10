import pytest

from americano import parse, ParseError


"""
List of parameters to test. Follows the function signature: f(expression, expected, context={})
"""
test_eval_parameters = [
    # Literals
    ['\"\\"\"', '"'],
    ["\'\\'\'", "'"],
    ['"4"', '4'],
    ["'4'", '4'],
    ['"with space"', 'with space'],
    ["'with space'", 'with space'],
    ['"A"', 'A'],
    ["'A'", 'A'],
    ['"+"', '+'],
    ["'+'", '+'],
    ['"$var"', '$var'],
    ["'$var'", '$var'],
    ['1', 1],
    ['100', 100],
    ['0.0', 0.0],
    ['0.12', 0.12],
    ['12.0', 12.0],
    ['12.34', 12.34],
    ['true', True],
    ['false', False],
    ['null', None],
    # Variables
    ['var', 1, {'var': 1}],
    ['var', 'A', {'var': 'A'}],
    ['var1 + var2', 3, {'var1': 1, 'var2': 2}],
    # Arithmetic operators
    ['1 + 2', 3],
    ['1.2 + 3', 4.2],
    ['1.2 + 3.4', 4.6],
    ['"A" + "B"', 'AB'],
    ['null + "A"', 'nullA'],
    ['"A" + null', 'Anull'],
    ['"A" + var', 'Anull', {'var': None}],
    ['"A" + 1', 'A1'],
    ['"A" + true', 'Atrue'],
    ['"A" + false', 'Afalse'],
    ['1 + true', 2],
    ['1 + false', 1],
    ['true + false', 1],
    ['1 - 2', -1],
    ['1.2 - 3', -1.8],
    ['1.2 - 3.4', -2.2],
    ['2 - 1', 1],
    ['3 - 1.2', 1.8],
    ['3.4 - 2.2', 1.2],
    ['"2" - 1', 1],
    ['"2.5" - 1', 1.5],
    ['2 * 3', 6],
    ['2.1 * 3', 6.3],
    ['2.1 * 3.5', 7.35],
    ['true * 5', 5],
    ['false * 5', 0],
    ['null * 5', 0],
    ['"3" * 5', 15],
    ['6 / 3', 2.0],
    ['5 / 2', 2.5],
    ['2.6 / 2', 1.3],
    ['6 / 2.4', 2.5],
    ['10 / "2"', 5],
    # Unary operators
    ['-1', -1],
    ['+1', 1],
    ['+1.7', 1.7],
    ['+"1"', 1],
    ['+"1.5"', 1.5],
    ['+true', 1],
    ['+false', 0],
    ['+null', 0],
    ['!true', False],
    ['!false', True],
    ['!0', True],
    ['!1', False],
    # Logic operators
    ['true && true', True],
    ['true && false', False],
    ['false && true', False],
    ['false && false', False],
    ['1 && 1', 1],
    ['1 && 0', 0],
    ['0 && 1', 0],
    ['0 && 0', 0],
    ['true || true', True],
    ['true || false', True],
    ['false || true', True],
    ['false || false', False],
    ['1 || 1', 1],
    ['1 || 0', 1],
    ['0 || 1', 1],
    ['0 || 0', 0],
    # Comparison operators
    ['1 < 2', True],
    ['2 < 1', False],
    ['2 < 2', False],
    ['1 <= 2', True],
    ['2 <= 1', False],
    ['2 <= 2', True],
    ['1 >= 2', False],
    ['2 >= 1', True],
    ['2 >= 2', True],
    ['1 > 2', False],
    ['2 > 1', True],
    ['2 > 2', False],
    ['1 === 1', True],
    ['1 === 2', False],
    ['1 === "1"', False],
    ['1 === 1.0', True],
    ['1 === true', False],
    ['"A" === "A"', True],
    ['"A" === "B"', False],
    ['null === null', True],
    ['null === 0', False],
    ['null === 1', False],
    ['1 == 1', True],
    ['1 == 2', False],
    ['1 == "1"', True],
    ['1 == 1.0', True],
    ['1 == true', True],
    ['null == null', True],
    ['null == 0', False],
    ['null == 1', False],
    ['"A" == "A"', True],
    ['"A" == "B"', False],
    ['"A" == 1', False],
    ['1 !== 1', False],
    ['1 !== 2', True],
    ['1 !== "1"', True],
    ['1 !== 1.0', False],
    ['1 !== true', True],
    ['null !== null', False],
    ['null !== 0', True],
    ['null !== 1', True],
    ['"A" !== "A"', False],
    ['"A" !== "B"', True],
    ['1 != 1', False],
    ['1 != 2', True],
    ['1 != "1"', False],
    ['1 != 1.0', False],
    ['1 != true', False],
    ['null != null', False],
    ['null != 0', True],
    ['null != 1', True],
    ['"A" != "A"', False],
    ['"A" != "B"', True],
    # Parentheses
    ['(1)', 1],
    ['(1 + 2)', 3],
    ['((1))', 1],
    ['(1 + 2) * (3 + 7)', 30],
    ['(var)', 1, {'var': 1}],
    ['([1])', [1]],
    ['[(1)]', [1]],
    # Array
    ['[]', []],
    ['[1]', [1]],
    ['[1,]', [1]],
    ['[1, 2]', [1, 2]],
    ['[1, 2] == [1, 2]', True],
    ['[1, 2] == var', True, {'var': [1, 2]}],
    ['[1, 2] == var', False, {'var': [0]}],
    # Precedence
    ['3 + 4 - 2', 5],
    ['4 - 2 + 3', 5],
    ['6 / 3 * 4', 8],
    ['3 * 4 / 6', 2],
    ['1 + 2 * 3', 7],
    ['2 * 3 + 1', 7],
    ['1 - 2 * 3', -5],
    ['2 * 3 - 1', 5],
    ['1 + 6 / 2', 4],
    ['6 / 2 + 1', 4],
    ['-1 + 3', 2],
    ['3 + -1', 2],
    ['true !== true || true', True],
    ['3 === 2 + 1', True],
    ['4 * (1 + 2)', 12],
    ['3 * (1 + (5 * 7))', 108],
    ['is_true(true)', True, {'is_true': lambda x: x is True}],
    ['is_true(false)', False, {'is_true': lambda x: x is True}],
    ['true ? "a" : "b"', 'a'],
    ['false ? "a" : "b"', 'b'],
]

for parameter_list in test_eval_parameters:
    if len(parameter_list) == 2:
        parameter_list.append({})


@pytest.mark.parametrize('expression,expected,context', test_eval_parameters)
def test_eval(expression, expected, context):
    expected = pytest.approx(expected) if isinstance(expected, float) else expected
    p = parse(expression)
    result = p.eval(context)
    assert result == expected


def test_no_nud():
    with pytest.raises(ParseError):
        parse('?')