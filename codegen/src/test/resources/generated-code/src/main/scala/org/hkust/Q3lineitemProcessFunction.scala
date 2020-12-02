import scala.math.Ordered.orderingToOrdered
import org.hkust.BasedProcessFunctions.RelationFKCoProcessFunction
import org.hkust.RelationType.Payload
import java.util.Date
class Q3lineitemProcessFunction extends RelationFKCoProcessFunction[Any]("lineitem",1,Array("ORDERKEY"),Array("ORDERKEY"),true, true) {
override def isValid(value: Payload): Boolean = {
   if(value("SHIPDATE").asInstanceOf[java.util.Date]>format.parse("1995-03-15")){
   true}else{
   false}
}
}