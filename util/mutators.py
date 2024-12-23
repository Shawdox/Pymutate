import random
import libcst as cst
from libcst.tool import dump

random.seed(1)
p = 1

def randomString(length):
    baseStr = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.sample(baseStr, length))

class For2While(cst.CSTTransformer):
    def leave_For(self, original_node: cst.For, updated_node: cst.For):
        # Extract the target, iterable, and body
        target = original_node.target
        iterable = original_node.iter
        body = original_node.body.body
        #print(iterable)

        # Create the new while structure
        list_var = cst.Name("list_" + randomString(4))
        idx_var = cst.Name("idx_" + randomString(4))
        # idx = 0
        idx_init = cst.Assign(
            targets=[cst.AssignTarget(idx_var)],
            value=cst.Integer("0"),
        )
        # idx < len(list)
        while_condition = cst.Comparison(
            left=idx_var,
            comparisons=[
                cst.ComparisonTarget(
                    cst.LessThan(), 
                    cst.Call(
                        func=cst.Name("len"),
                        args=[cst.Arg(value=list_var)],
                    )
                )
            ]
        )   
        # list = [iter]
        if isinstance(iterable, cst.Call):
            if iterable.func.value == "enumerate" or \
                (hasattr(iterable.func, "attr") and iterable.func.attr.value == "items"):
                list_assign = cst.SimpleStatementLine(
                    body = [cst.Assign(
                        targets=[cst.AssignTarget(list_var)],
                        value=cst.Call(
                                func=cst.Name(value='list'),
                                args=[cst.Arg(iterable)],
                            ),
                    )]
                )        
            else: 
                list_assign = cst.SimpleStatementLine(
                    body = [cst.Assign(
                        targets=[cst.AssignTarget(list_var)],
                        value=iterable,
                    )]
                )
        else:
            list_assign = cst.SimpleStatementLine(
                body = [cst.Assign(
                    targets=[cst.AssignTarget(list_var)],
                    value=iterable,
                )]
            )
        # idx = idx + 1
        increment_i = cst.SimpleStatementLine(
            body = [cst.Assign(
                targets=[cst.AssignTarget(idx_var)],
                value=cst.BinaryOperation(left=idx_var, right=cst.Integer("1"), operator=cst.Add()),
            )]
        )
        # i = list[idx]
        target_init = cst.SimpleStatementLine(
            body = [cst.Assign(
                targets=[cst.AssignTarget(target)],
                value=cst.Subscript(value=list_var, slice=[cst.SubscriptElement(slice=cst.Index(value=idx_var))]),
                )
            ]
        )
        return cst.FlattenSentinel([
            cst.SimpleStatementLine(body=[idx_init]), # idx = 0
            list_assign, # list = [iter]
            cst.While(test=while_condition, # idx < len(list)
                    body=cst.IndentedBlock(
                        body=[target_init] + list(updated_node.body.body) + [increment_i]
                    )
                  )
        ])

# x += 1 --> x = x + 1
class AugAssign2Assign(cst.CSTTransformer):
    def leave_AugAssign(self, original_node: cst.AugAssign, updated_node: cst.AugAssign):
        target = original_node.target
        operator = original_node.operator
        value = original_node.value
        
        if isinstance(operator, cst.AddAssign):
            new_operator = cst.Add()
        elif isinstance(operator, cst.SubtractAssign):
            new_operator = cst.Subtract()
        elif isinstance(operator, cst.MultiplyAssign):
            new_operator = cst.Multiply()
        elif isinstance(operator, cst.DivideAssign):
            new_operator = cst.Divide()      
        elif isinstance(operator, cst.ModuloAssign):
            new_operator = cst.Modulo()   
        elif isinstance(operator, cst.BitXorAssign):
            new_operator = cst.BitXor()
        elif isinstance(operator, cst.FloorDivideAssign):
            new_operator = cst.FloorDivide()
        elif isinstance(operator, cst.BitAndAssign):
            new_operator = cst.BitAnd()
        elif isinstance(operator, cst.BitOrAssign):
            new_operator = cst.BitOr()
        elif isinstance(operator, cst.LeftShiftAssign):
            new_operator = cst.LeftShift()
        elif isinstance(operator, cst.RightShiftAssign):
            new_operator = cst.RightShift()
        assign = cst.Assign(
            targets = [cst.AssignTarget(target)],
            value = cst.BinaryOperation(
                left = target,
                operator = new_operator,
                right = value,
            )
        )
        return cst.FlattenSentinel([assign])

# x = y --> x = y if 1>0 else z
# Each assignment operation has a probability p of being converted
class Assign2Ternary(cst.CSTTransformer):
    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign):
        #p = 0.5
        if random.random() <= p:
            Assign_targets = original_node.targets
            Assign_value = original_node.value
            # rnd2 > rnd1
            rnd1 = random.randint(0, 9)
            rnd2 = random.randint(rnd1+1, 10)
            ternary = cst.IfExp(
                test = cst.Comparison(
                    left = cst.Integer(value = str(rnd2)),
                    comparisons = [
                        cst.ComparisonTarget(
                            #operator = cst.GreaterThan(),
                            operator = cst.LessThan(),
                            comparator = cst.Integer(value = str(rnd1)),
                        )
                    ]
                ),
                body = cst.Integer(value = '0'),
                orelse = Assign_value,
            )
            return cst.FlattenSentinel([cst.Assign(
                targets = Assign_targets,
                value = ternary,
            )])
        else:
            return original_node
        
# Random add random independent variable like: var_9tl = 59
# At random location
class Add_IndependentVar(cst.CSTTransformer):
    def leave_IndentedBlock(self, original_node: cst.IndentedBlock, updated_node: cst.IndentedBlock):
            #p = 0.5
            if random.random() <= p:
                dead_assign =  cst.Assign(
                    targets = [cst.AssignTarget(cst.Name('var_'+randomString(3)))],
                    value = cst.Integer(value = str(random.randint(0,100)))
                )
                #dead_assign =  cst.Assign(
                #    targets = [cst.AssignTarget(cst.Name('var'))],
                #    value = cst.Integer(value = str(111)),
                #)
                body = original_node.body
                # Choice an index randomly
                idx = random.randint(1, len(body))
                new_block = list(body[:idx]) + [cst.SimpleStatementLine(body = [dead_assign])] + list(body[idx:])
                return cst.IndentedBlock(body = cst.FlattenSentinel(new_block))
            else:
                return original_node

# a = b + c --> a = b; a = a + c
class AssignUnfoldding(cst.CSTTransformer):
    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign):
        p = 1
        if random.random() <= p:
            Assign_targets = original_node.targets[0]
            Assign_value = original_node.value
            if isinstance(Assign_value, cst.BinaryOperation):
                operator = Assign_value.operator
                right_b = Assign_value.left
                right_c = Assign_value.right
                
                if isinstance(right_b, cst.Name) and right_b.value == Assign_targets.target.value:
                    return original_node
                if isinstance(right_c, cst.Name) and right_c.value == Assign_targets.target.value:
                    return original_node
                
                # a = b
                assign_1 = cst.Assign(
                    targets = [Assign_targets,],
                    value = right_b,
                )
                # a = a + c
                assign_2 = cst.Assign(
                    targets = [Assign_targets,],
                    value = cst.BinaryOperation(
                        left = Assign_targets.target,
                        operator= operator,
                        right = right_c,
                    )
                )
                return cst.FlattenSentinel([
                    assign_1, 
                    assign_2,
                ])
            return original_node
        else:
            return original_node

# m = 0 --> m = 3 - 3
class ConstantUnfoldding(cst.CSTTransformer):
    '''
    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign):
        Assign_targets = original_node.targets[0]
        Assign_value = original_node.value
        if isinstance(Assign_value, cst.Integer):
            num = int(Assign_value.value)
            randnum = random.randint(1, 100)
            num = num - randnum
            if num >= 0:
                new_assign = cst.Assign(
                    targets = [Assign_targets],
                    value = cst.BinaryOperation(
                            left = cst.Integer(value = str(randnum)),
                            operator= cst.Add(),
                            right = cst.Integer(value = str(num)),
                            lpar = [cst.LeftParen(),],
                            rpar = [cst.RightParen(),],
                        )
                )
            else:
                new_assign = cst.Assign(
                    targets = [Assign_targets],
                    value = cst.BinaryOperation(
                            left = cst.Integer(value = str(randnum)),
                            operator= cst.Add(),
                            right = cst.UnaryOperation(
                                operator = cst.Minus(),
                                expression = cst.Integer(value = str(-1*num)),
                            ),
                            lpar = [cst.LeftParen(),],
                            rpar = [cst.RightParen(),],
                        )
                )
            return cst.FlattenSentinel([new_assign,])
        return original_node
    '''
    def leave_Integer(self, original_node: cst.Integer, updated_node: cst.Integer):
        if original_node.value[:2] == '0x' or original_node.value[:2] == '0X':
            return original_node
        num = int(original_node.value)
        randnum = random.randint(1, 100)
        num = num - randnum
        if num >= 0:
            return cst.BinaryOperation(
                            left = cst.Integer(value = str(randnum)),
                            operator= cst.Add(),
                            right = cst.Integer(value = str(num)),
                            lpar = [cst.LeftParen(),],
                            rpar = [cst.RightParen(),],
                        )
        else:
            return cst.BinaryOperation(
                            left = cst.Integer(value = str(randnum)),
                            operator= cst.Add(),
                            right = cst.UnaryOperation(
                                operator = cst.Minus(),
                                expression = cst.Integer(value = str(-1*num)),
                            ),
                            lpar = [cst.LeftParen(),],
                            rpar = [cst.RightParen(),],
                        )

class IfReverse(cst.CSTTransformer):
    def leave_If(self, original_node: cst.If, updated_node: cst.If):
        test = original_node.test
        body = original_node.body
        if original_node.orelse == None:
            return original_node
        orelse = original_node.orelse
        if isinstance(orelse, cst.Else):
            new_body = orelse.body
        elif isinstance(orelse, cst.If):
            new_body = cst.IndentedBlock(body = [orelse,])
        else:
            return original_node
        new_test = cst.UnaryOperation(
            operator = cst.Not(),
            expression = test,
        )
        newIf = cst.If(
            test = new_test,
            body = new_body,
            orelse = cst.Else(body = body),
        )
        return newIf

def TrueExpression():
    # ((True or False) and (False or True))
    candidate1 = cst.BooleanOperation(
        left = cst.BooleanOperation(
            left = cst.Name(value = 'True'),
            operator = cst.Or(),
            right = cst.Name(value = 'False'),
            lpar=[cst.LeftParen(),],
            rpar=[cst.RightParen(),],
        ),
        operator = cst.And(),
        right = cst.BooleanOperation(
            left = cst.Name(value = 'False'),
            operator = cst.Or(),
            right = cst.Name(value = 'True'),
            lpar=[cst.LeftParen(),],
            rpar=[cst.RightParen(),],
        ),
        lpar=[cst.LeftParen(),],
        rpar=[cst.RightParen(),],
    )
    # (5 > 3)
    rand1 = random.randint(2,10)
    rand2 = random.randint(0,rand1-1)
    candidate2 = cst.Comparison(
        left = cst.Integer(value=str(rand1)),
        comparisons = [cst.ComparisonTarget(
            operator = cst.GreaterThan(),
            comparator = cst.Integer(value = str(rand2)),
        )],
        lpar=[cst.LeftParen(),],
        rpar=[cst.RightParen(),],
    )
    # (7 < 4)
    rand3 = random.randint(2,10)
    rand4 = random.randint(0,rand1-1)
    candidate2_re = cst.Comparison(
        left = cst.Integer(value=str(rand1)),
        comparisons = [cst.ComparisonTarget(
            operator = cst.LessThan(),
            comparator = cst.Integer(value = str(rand2)),
        )],
        lpar=[cst.LeftParen(),],
        rpar=[cst.RightParen(),],
    )
    #candidates = [candidate1, candidate2]
    
    compound_expression = cst.BooleanOperation(
        left = candidate1,
        operator = cst.And(),
        right = cst.BooleanOperation(
            left = candidate2,
            operator = cst.Or(),
            right = candidate2_re,
            lpar=[cst.LeftParen(),],
            rpar=[cst.RightParen(),],
        ),
        lpar=[cst.LeftParen(),],
        rpar=[cst.RightParen(),],
    )
    
    return compound_expression

class IfAddShortCircuiting(cst.CSTTransformer):
    def leave_If(self, original_node: cst.If, updated_node: cst.If):
        test = original_node.test
        body = original_node.body
        orelse = original_node.orelse
        
        new_test = cst.BooleanOperation(
            left = test,
            operator = cst.And(),
            right = TrueExpression(),
        )
        return cst.If(
            test = new_test,
            body = body,
            orelse = orelse,
        )

class StringUnfoldding(cst.CSTTransformer):
    def leave_SimpleString(self, original_node: cst.SimpleString, updated_node: cst.SimpleString):
        value = original_node.value
        if len(value) <= 1 or value[0:2] in ["b'", 'b"', "f'", 'f"',  "r'", 'r"']:
            return original_node
        if value[0:3] == '"""':
            return original_node
        if value == '"\\n"' or value == "'\\n'":
            return original_node
        if value == '"\\t"' or value == "'\\t'":
            return original_node
        while True:
            randidx = random.randint(0, len(value)-1)
            if randidx>0:
                if value[randidx-1] != '\\' or value[randidx-1] != "\\":
                    break
            else:
                break
        str1 = value[0:randidx]
        str2 = value[randidx:len(value)]
        if str1 == '' or str1 == "":
            str1 = value[0] + value[0]
        elif (str1[-1] != value[0]) or len(str1) == 1 or randidx != len(value)-1:
            str1 += value[0]
            
        if str2 == '' or str2 == "":
            str2 = value[0] + value[0]
        elif str2[0] != value[0] or len(str2) == 1:
            str2 = value[0] + str2        
        str1 = cst.SimpleString(value=str1)
        str2 = cst.SimpleString(value=str2)
        
        return cst.BinaryOperation(
            left = str1,
            operator= cst.Add(),
            right= str2,
            lpar = [cst.LeftParen(),],
            rpar = [cst.RightParen(),],
        )
         

def mutate(code, mutator):
    tree = cst.parse_module(code)
    transformed_tree = tree.visit(mutator())
    return transformed_tree.code