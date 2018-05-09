module Main where

import Language.Python.Common.AST
import Language.Python.Common.Pretty
import Language.Python.Common.PrettyAST
import Language.Python.Common.SrcLocation
import Language.Python.Version3.Parser
import System.Environment
import System.Exit
import System.IO

type CheckResult = Either String ()

good :: CheckResult
good = Right ()

bad :: (Pretty (t SrcSpan), Annotated t) => t SrcSpan -> CheckResult
bad a =
  Left $ "unsupported " ++ show (pretty a) ++ " at " ++ show (pretty (annot a))

validOp :: Op SrcSpan -> CheckResult
validOp op@(In _) = bad op
validOp op@(Is _) = bad op
validOp op@(IsNot _) = bad op
validOp op@(NotIn _) = bad op
validOp _ = good

validExpr :: Expr SrcSpan -> CheckResult
validExpr e = bad e

variableExpr :: Expr SrcSpan -> CheckResult
variableExpr (Var _ _) = good
variableExpr e = bad e

validArgument :: Argument SrcSpan -> CheckResult
validArgument (ArgExpr e _) = validExpr e
validArgument a = bad a
    
validStatementDecorator :: Decorator SrcSpan -> CheckResult
validStatementDecorator d = bad d

validStatement :: Statement SrcSpan -> CheckResult
-- We assume a specific set of modules is already imported
{-
validStatement (While _ _ _ _) = validWhile
validStatement (For _ _ _ _ _) = validFor
validStatement (Fun _ _ _ _ _) = validFun
-}
validStatement (Conditional guards elseBody _) = do
  mapM_ (validExpr . fst) guards
  mapM_ (validSuite . snd) guards
  validSuite elseBody
validStatement (Assign es e _) = do
    mapM_ variableExpr es >> validExpr e
validStatement (AugmentedAssign l _ r _) =
  variableExpr l >> validExpr r
validStatement s@(Assert es _) = bad s --all validAssert es
validStatement (Decorated ds s _) = mapM_ validStatementDecorator ds
validStatement (Return me _) = maybe good validExpr me
--validStatement (Raise e _) = validRaiseExpr e
validStatement (Pass _) = good
validStatement s = bad s

validSuite :: Suite SrcSpan -> CheckResult
validSuite = mapM_ validStatement

validParameter :: Parameter SrcSpan -> CheckResult
validParameter (Param _ _ Nothing _) = good
validParameter p = bad p

validTopStatement :: Statement SrcSpan -> CheckResult
validTopStatement (Fun _ ps _ body _) =
  mapM_ validParameter ps >> validSuite body
validTopStatement s = bad s

validModule :: Module SrcSpan -> CheckResult
validModule (Module ss) = mapM_ validTopStatement ss

exitFail :: String -> IO ()
exitFail msg = hPutStrLn stderr msg >> exitWith (ExitFailure 1)

checkFile :: String -> IO ()
checkFile filename = do
  text <- readFile filename
  case parseModule text filename of
    Left err -> exitFail $ "Parse error: " ++ show err
    Right (m, _) -> do
      putStrLn "Parse succeeded!"
      let status = case validModule m of
                     Right () -> "valid"
                     Left msg -> "NOT valid: " ++ msg
      putStrLn $ "File is " ++ status

main :: IO ()
main = do
  args <- getArgs
  case args of
    [filename] -> checkFile filename
    _ -> exitFail "Usage: spec-checker <filename>"
