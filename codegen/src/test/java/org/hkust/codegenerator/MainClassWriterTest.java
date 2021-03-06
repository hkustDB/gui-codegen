package org.hkust.codegenerator;

import org.ainslec.picocog.PicoWriter;
import org.hkust.objects.AggregateProcessFunction;
import org.hkust.objects.Node;
import org.hkust.objects.RelationProcessFunction;
import org.hkust.schema.Attribute;
import org.hkust.schema.Relation;
import org.hkust.schema.RelationSchema;
import org.jetbrains.annotations.NotNull;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.junit.MockitoJUnitRunner;

import java.util.Collections;
import java.util.Date;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
public class MainClassWriterTest {

    @Mock
    private AggregateProcessFunction aggregateProcessFunction;

    @Mock
    private RelationProcessFunction relationProcessFunction;

    @Mock
    private Relation relation;

    @Mock
    private Node node;

    @Mock
    private RelationSchema schema;

    @Before
    public void initialization() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void addMainFunctionTest() {
        PicoWriter picoWriter = new PicoWriter();
        MainClassWriter mainClassWriter = getMainClassWriter();
        mainClassWriter.addMainFunction(picoWriter);

        assertEquals(picoWriter.toString().replaceAll("\\s+", ""), ("def main(args: Array[String]) {\n" +
                "   val env = StreamExecutionEnvironment.getExecutionEnvironment\n" +
                "   val params: ParameterTool = ParameterTool.fromArgs(args)\n" +
                "   env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime)\n" +
                "   var executionConfig = env.getConfig\n" +
                "   executionConfig.enableObjectReuse()\n" +
                "   val inputpath = \"flinkInput\"\n" +
                "   val outputpath = \"flinkOutput\"\n" +
                "   val inputStream : DataStream[Payload] = getStream(env,inputpath)\n" +
                "   val result  = inputStream.keyBy(i => i._3)\n" +
                "   .process(new relationProcessFunctionProcessFunction())\n" +
                "   .keyBy(i => i._3)\n" +
                "   .process(new aggregateProcessFunctionProcessFunction)\n" +
                "   .map(x => (x._4.mkString(\", \"), x._5.mkString(\", \"), x._6))\n" +
                "   .writeAsText(outputpath,FileSystem.WriteMode.OVERWRITE)\n" +
                "   .setParallelism(1)\n" +
                "   env.execute(\"Flink Streaming Scala API Skeleton\")\n" +
                "}").replaceAll("\\s+", ""));
    }

    @Test
    public void addGetStreamFunctionTest() throws Exception {
        PicoWriter picoWriter = new PicoWriter();
        MainClassWriter mainClassWriter = getMainClassWriter();
        when(relationProcessFunction.getRelation()).thenReturn(relation);
        when(relation.getValue()).thenReturn("relation");
        mainClassWriter.addGetStreamFunction(picoWriter);

        assertEquals(picoWriter.toString().replaceAll("\\s+", ""), ("private def getStream(env: StreamExecutionEnvironment, dataPath: String): DataStream[Payload] = {\n" +
                "   val data = env.readTextFile(dataPath).setParallelism(1)\n" +
                "   val format = new java.text.SimpleDateFormat(\"yyyy-MM-dd\")\n" +
                "   var cnt : Long = 0\n" +
                "   val restDS : DataStream[Payload] = data\n" +
                "   .map(line => {\n" +
                "   val header = line.substring(0,3)\n" +
                "   val cells : Array[String] = line.substring(3).split(\"\\\\|\")\n" +
                "   val i = Tuple0()\n" +
                "   var relation = \"\"\n" +
                "   var action = \"\"\n" +
                "   header match {\n" +
                "   case \"+LI\" =>\n" +
                "   relation = \"relation\"\n" +
                "   action = \"Insert\"\n" +
                "   case \"-LI\" =>\n" +
                "   relation = \"relation\"\n" +
                "   action = \"Delete\"\n" +
                "   }\n" +
                "   cnt = cnt + 1\n" +
                "   Payload(relation, action,\n" +
                "   Tuple2(cells(0).toInt, cells(3).toInt).asInstanceOf[Any],\n" +
                "   Array(),\n" +
                "   Array(), cnt)\n" +
                "   }).setParallelism(1).filter(x => x._1 != \"\").setParallelism(1)\n" +
                "   restDS\n" +
                "}\n").replaceAll("\\s+", ""));
    }

    @Test
    public void attributeCodeTest() {
        MainClassWriter mainClassWriter = getMainClassWriter();
        Attribute mockAttribute1 = new Attribute(Integer.class, 0, "attribute1");
        Attribute mockAttribute2 = new Attribute(Date.class, 1, "attribute2");
        StringBuilder columnNamesCode = new StringBuilder();
        StringBuilder tupleCode = new StringBuilder();

        //mainClassWriter.attributeCode(Relation.LINEITEM, new HashSet<>(Arrays.asList(mockAttribute1, mockAttribute2)), columnNamesCode, tupleCode);

        String columnsResult = columnNamesCode.toString();
        //Order of printed code isn't guaranteed so check for contains and do not tightly couple the exact string
        assertTrue(columnsResult.contains("ATTRIBUTE1") && columnsResult.contains("ATTRIBUTE2"));

        String tupleResult = tupleCode.toString();
        assertTrue(tupleResult.contains("cells(0).toInt") && tupleResult.contains("format.parse(cells(1))"));
    }

    @NotNull
    private MainClassWriter getMainClassWriter() {
        when(node.getAggregateProcessFunctions()).thenReturn(Collections.singletonList(aggregateProcessFunction));
        when(node.getRelationProcessFunctions()).thenReturn(Collections.singletonList(relationProcessFunction));
        when(aggregateProcessFunction.getName()).thenReturn("aggregateProcessFunction");
        when(relationProcessFunction.getName()).thenReturn("relationProcessFunction");
        return new MainClassWriter(node, schema, "flinkInput", "flinkOutput");
    }

}
