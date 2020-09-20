import org.ainslec.picocog.PicoWriter;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

import static java.util.Objects.requireNonNull;

public class RelationProcessFunctionWriter implements CodeGenerator {
    private final String className;
    private final String relationName;
    private final PicoWriter writer;
    private final RelationProcessFunction relationProcessFunction;

    public RelationProcessFunctionWriter(final RelationProcessFunction relationProcessFunction) {
        requireNonNull(relationProcessFunction);
        this.relationProcessFunction = relationProcessFunction;
        this.relationName = relationProcessFunction.getName();
        this.className = relationProcessFunction.getName() + "ProcessFunction";
        this.writer = new PicoWriter();
    }

    @Override
    public void generateCode(final String filePath) throws IOException {
        CheckerUtils.checkNullOrEmpty(filePath, "filePath");
        addImports();
        makeConstructor();
        makeIsValidFunction(relationProcessFunction.getSelectConditions(), "value");
        writer.writeln_r("}");
        Files.write(Paths.get(filePath + File.separator + className + ".scala"), writer.toString().getBytes());
    }

    private void makeConstructor() {

        String stringBuilder = "class " + className + " extends RelationFKProcessFunction[Any](\"" +
                relationName + "\"," +
                "Array()" + "," +
                "Array()" + "," +
                "true)" +
                "{";
        writer.writeln(stringBuilder);
    }

    private void makeIsValidFunction(List<SelectCondition> selectConditions, String param) {
        writer.writeln_r("override def isValid(value: Payload): Boolean = {");
        StringBuilder ifCondition = new StringBuilder();
        ifCondition.append("if(");
        SelectCondition condition;
        for (int i = 0; i < selectConditions.size(); i++) {
            ifCondition.append(param);
            condition = selectConditions.get(i);
            //Ensure that in the values list the attribute value is always added first
            Expression expression = condition.getExpression();
            AttributeValue attributeValue = (AttributeValue) expression.getValues().get(0);
            ConstantValue constantValue = (ConstantValue) expression.getValues().get(1);
            ifCondition.append("(\"").append(attributeValue.getName().toUpperCase()).append("\")");
            Class type = constantValue.getType();
            ifCondition.append(".asInstanceOf[")
                    //Needed to add fully qualified name of Date class but not others
                    .append(type.getSimpleName().equals("Date") ? type.getName() : type.getSimpleName())
                    .append("]")
                    //operator of the select condition itself
                    .append(expression.getOperator().getValue());

            if (type.equals(Type.getClass("date"))) {
                //Needed so generated code parses the date
                ifCondition.append("format.parse(\"").append(constantValue.getValue()).append("\")");
            } else if (type.equals(Type.getClass("string"))) {
                ifCondition.append("\"").append(constantValue.getValue()).append("\"");
            } else {
                ifCondition.append(constantValue.getValue());
            }

            if (i < selectConditions.size() - 1) {
                //operator that binds each select condition
                ifCondition.append(condition.getOperator().getValue());

            }
        }

        writer.write(ifCondition.toString());
        writer.writeln_r("){");
        writer.write("true");
        writer.writeln_lr("}else{");
        writer.write("false");
        writer.writeln_l("}");
        writer.writeln_l("}");
    }

    private void addImports() {
        writer.writeln("import scala.math.Ordered.orderingToOrdered");
        writer.writeln("import org.hkust.BasedProcessFunctions.RelationFKProcessFunction");
        writer.writeln("import org.hkust.RelationType.Payload");
    }

}