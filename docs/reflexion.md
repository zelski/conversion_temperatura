# Reflexión

> Escribir una reflexión sobre los aprendizajes obtenidos

Considerando todo lo visto durante el módulo desarrollaré la reflexión sobre los tópicos que más llamaron mi atención

## Cómo funciona la IA (a grandes rasgos)

El conocer cómo funciona la IA desde abajo, de cómo se transforman y usan los tókens y todo termina siendo una probabilística basada en números y en la cercanía semántica de las palabras para inferir cuál sería el siguiente token fue muy revelador, a partir de ahí puede uno entender el porqué de la elevado carga computacional que requiere la IA, también nos hace darnos cuenta de la importancia de establecer un buen contexto (más palabras no precisamente significa mejor contexto), al conocer que la ventana de contexto tiene un limite también nos muestra que hay que usar con sabiduria ese espacio ya que si bien hoy en día esa ventana cada vez es mas grande hay que considerar que no es infinito, que procesar mas tokens cuesta mas, y que podemos llegar a un punto en que la IA puede empezar a delirar.

## Claude como agente

Antes de este certificado había tenido un ligero acercamiento a Claude y ninguno con alguna API, por lo que al inicio fue interesante ver cómo era la interacción con la IA antes de los agentes, ver a la IA como un cerebro que carece de extremidades para llevar a cabo las tareas que derivan de su "pensamiento", entender que a partir de la interacción con la IA, que nos devuelve texto, hay que ejecutar acciones con otras herramientas, como en el caso de colab que se tenía código en python. Claude ha empaquetado todo esto, durante el reto me sorprendió que al no tener acceso a github mediante credenciales ssh o algo parecido, me sugirió utilizar un navegador que trae integrado, yo solo inicié sesión y luego Claude pudo actuar con total autonomía para operar github, crear/aprobar/mergear PRs.

## Autonomía de Claude

Claude me sorprendió por el grado de autonomía que mostró, hizo cosas más allá de lo pedido, por ejemplo, cuando le pedí un análisis superficial del código para entenderlo no solo me dijo que hace el código, también identificó los bugs o mejoras que se le podrían hacer, yo no le tuve que decir que considerada que cualquier cambio debía contemplar los tests, que los debía correr para que pasaran y si no pasaban tenía que corregir el código, incluso sabía que debía modificar las pruebas si no pasaban o si dejaban de tener sentido. En cuanto a nivel de análisis y propuestas creo que esto tiene un beneficio porque nos hace ver cosas que no teníamos en el radar, pero sin duda hay que tener cuidado a la hora de ejecutar tareas.

## Enfoque human-first vs enfoque de pruebas

Este es uno de los temás que más me interesa, todo es tan nuevo con la IA, me parece que aun nadie tiene claro cómo deberíamos trabajar con ella, hay preocupaciones por la deuda cognitiva que podríamos generar al depender tanto de ella, se habla de los problemas que vamos a tener en el futuro cuando hoy en día permitimos (o alentamos) que los desarrolladores jr le dejen la carga del desarrollo de código a la IA y que se enfoquen mas en entender de procesos de una empresa y su modelo de negocio, porque entonces esas "batallas" que se tenían al hacer debug sobre un código, a entender porqué y cómo hacer una optimización en una consulta sql o una API REST para mejorar el P99, son el camino que nos da el expertise para entender si algo está bien hecho o no, y por ende poder "supervisar" el trabajo de la IA.

Dentro del enfoque [human first](https://humanfirstengineering.dev/manifesto) se habla de "we own what we ship", parafraseando dice que solo los humanos son responsables de la calidad, claridad y seguridad de los cambios, que cada cambio debe tener un humano responsable que sepa y pueda explicarlo, esto yo lo traduzco a que si el código que hace la IA no lo puedes entender/explicar entonces no lo puedes llevar a producción. Por otro lado se viene impulsando el spec-driven-development, donde (hasta donde entiendo) el trabajo se enfoca en definir todos los aspectos funcionales y no funcionales para que los agentes siempre produzcan un código que aunque no sea el mismo ejecución tras ejecución, si cumpla con las especificaciones, se siente como si el código pasara a segundo plano. También he leído un enfoque que se basa en tener bien claras y programadas las pruebas, y que si el código generado por la IA pasa dichas pruebas, entonces está bien.

Cuál será la mejor opción? supongo que como siempre, va a depender de lo que estemos resolviendo.